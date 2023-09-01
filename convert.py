import sys
import json

# Configuration
with open("config.json", "r") as config_file:
    config = json.load(config_file)

def clean_type(field_type: str) -> str:
    return field_type.replace("[", "").replace("]", "").replace("!", "")

def is_array(field_type: str) -> bool:
    return "[" in field_type and "]" in field_type

def is_nullable(field_type: str) -> bool:
    if is_array(field_type) and "!" in field_type.split(']')[0]:
        return False
    return "!" not in field_type

def transform_to_nestjs(schema: str, config: dict) -> (str, list):
    lines = schema.split("\n")
    class_name = lines[0].split(" ")[2]

    nestjs_imports = {"Field", "ObjectType"}
    custom_imports = set()
    nestjs_code = f"@ObjectType()\nexport class {class_name}\n"

    for line in lines[1:-1]:
        line = line.strip()

        if ":" not in line:
            continue

        field_name = line.split(":")[0].strip()
        field_type_raw = line.split(":")[1].strip().split(" ")[0]
        field_type = clean_type(field_type_raw)
        
        graphql_type = config['mapping'][field_type].get('convert', field_type) if field_type in config['mapping'] else field_type

        if field_type in config['mapping']:
            ts_type = config['mapping'][field_type]['typescriptType']
            if 'import' in config['mapping'][field_type]:
                custom_imports.add(config['mapping'][field_type]['import'])
            nestjs_code += f'  @Field(() => {graphql_type}, {{ nullable: {str(is_nullable(field_type_raw)).lower()} }})\n  {field_name}: {ts_type};\n\n'
        elif field_type in config['native_types']:
            ts_type = field_type
            nestjs_imports.add(ts_type)
            nestjs_code += f'  @Field(() => {graphql_type}, {{ nullable: {str(is_nullable(field_type_raw)).lower()} }})\n  {field_name}: {ts_type};\n\n'
        else:
            nestjs_code += f'  // TODO: Define and import the type {field_type}\n  // @Field(() => {graphql_type}, {{ nullable: {str(is_nullable(field_type_raw)).lower()} }})\n  // {field_name}: {field_type};\n\n'

    nestjs_code += "}"

    merged_imports = []
    if nestjs_imports:
        merged_imports.append(f"import {{ {', '.join(nestjs_imports)} }} from '@nestjs/graphql';")
    for custom_import in custom_imports:
        merged_imports.append(custom_import)

    return merged_imports + [nestjs_code]

def main(input_file: str, output_file: str):
    with open(input_file, 'r') as f:
        schema = f.read()

    nestjs_code = transform_to_nestjs(schema, config)

    with open(output_file, 'w') as f:
        f.write("\n".join(nestjs_code))

    print(f"Output written to {output_file}")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python script_name.py <input_schema_filepath> <output_filepath>")
        sys.exit(1)

    input_filepath = sys.argv[1]
    output_filepath = sys.argv[2]

    main(input_filepath, output_filepath)
