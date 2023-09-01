import json
import re
import os

def clean_type(type_string):
    return type_string.replace("!", "").replace("[", "").replace("]", "")

def is_nullable(type_string):
    return not "!" in type_string

def extract_graphql_classes(schema_filepath):
    with open(schema_filepath, 'r') as file:
        data = file.read().replace('\n', ' ')
        data = re.sub(r'//.*', '', data)  # Remove comments
    blocks = re.findall(r'type (.*?) { (.*?)}', data)
    return blocks

def extract_fields(block_content):
    return re.findall(r'(\w+):\s*([\w\[\]!]+)', block_content)

def transform_to_nestjs(block, config):
    class_name = block[0]
    fields = extract_fields(block[1])

    imports = {"Field", "ObjectType"}
    custom_imports = set()

    nestjs_code = []

    for field in fields:
        field_name = field[0]
        field_type_raw = field[1]
        field_type = clean_type(field_type_raw)

        if field_type in config['mapping']:
            ts_type = config['mapping'][field_type].get('convert', field_type)
            nestjs_code.append(f'  @Field(() => {ts_type}, {{ nullable: {str(is_nullable(field_type_raw)).lower()} }})')
            nestjs_code.append(f'  {field_name}: {config["mapping"][field_type]["typescriptType"]};')
            nestjs_code.append('')  # Add a blank line for spacing
            if 'import' in config['mapping'][field_type]:
                custom_imports.add(config['mapping'][field_type]['import'])
        else:
            nestjs_code.append(f'  // TODO: Define and import the type {field_type}')
            nestjs_code.append(f'  // @Field(() => {field_type}, {{ nullable: {str(is_nullable(field_type_raw)).lower()} }})')
            nestjs_code.append(f'  // {field_name}: {field_type};')
            nestjs_code.append('')  # Add a blank line for spacing

    for native_type in config["native_types"]:
        if native_type in "\n".join(nestjs_code):
            imports.add(native_type)

    import_string = f"import {{ {', '.join(imports)} }} from '@nestjs/graphql';"
    if custom_imports:
        import_string += "\n" + "\n".join(custom_imports)
    return [import_string, '', f"@ObjectType()", f"export class {class_name} {{"] + nestjs_code + ["}"]



def main(input_filepath, output_dir):
    with open('config.json') as config_file:
        config = json.load(config_file)

    blocks = extract_graphql_classes(input_filepath)
    for block in blocks:
        class_name = block[0]
        output_code = transform_to_nestjs(block, config)
        with open(os.path.join(output_dir, f"{class_name}.dto.ts"), 'w') as output_file:
            for line in output_code:
                output_file.write(f"{line}\n")

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 3:
        print("Usage: python3 convert.py <input_schema_filepath> <output_directory>")
        sys.exit(1)

    main(sys.argv[1], sys.argv[2])
