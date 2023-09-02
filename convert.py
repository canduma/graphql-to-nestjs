import json
import os
import sys
import re
from collections import defaultdict

def transform_to_nestjs(schema_block, config, is_input=False):
    block_lines = schema_block.strip().split("\n")
    name = block_lines[0].split("{")[0].strip().split()[-1]

    if name in ["Mutation", "Query", "Subscription"]:
        return ""

    fields = block_lines[1:-1]

    imports = defaultdict(set)
    typescript_fields = []

    for i in range(0, len(fields)):
        field_data = fields[i].strip()
        split_data = field_data.split(":")
        
        if len(split_data) != 2:
            continue
        
        field_name, field_type_raw = map(str.strip, split_data)
        nullable = not field_type_raw.endswith("!")
        base_field_type = field_type_raw.replace("!", "").replace("[", "").replace("]", "").strip()
        field_type = field_type_raw.replace("!", "").strip()

        if base_field_type in config['mapping']:
            ts_type = config['mapping'][base_field_type]['typescriptType']
            if 'import' in config['mapping'][base_field_type]:
                imp = config['mapping'][base_field_type]['import']
                module, members = imp.split("{")[1].split("}")[0], imp.split("from")[1]
                imports[members.strip()].add(module.strip())

            field_str = f'  @Field(() => {field_type}, {{ nullable: {str(nullable).lower()} }})\n'
            field_str += f'  {field_name}: {ts_type};'
        else:
            field_str = f'  // TODO: Define and import the type {field_type}\n'
            field_str += f'  // @Field(() => {field_type}, {{ nullable: {str(nullable).lower()} }})\n'
            field_str += f'  // {field_name}: {field_type};'

        typescript_fields.append(field_str)

    imports["from '@nestjs/graphql';"].add("Field")
    if is_input:
        imports["from '@nestjs/graphql';"].add("InputType")
    else:
        imports["from '@nestjs/graphql';"].add("ObjectType")

    for native_type in config['native_types']:
        if native_type in schema_block and native_type != "String":
            imports["from '@nestjs/graphql';"].add(native_type)

    import_str = "\n".join(f"import {{ {', '.join(sorted(imp_set))} }} {imp_from}" for imp_from, imp_set in imports.items())

    decorator = "@InputType()" if is_input else "@ObjectType()"
    ts_code = f"{import_str}\n\n{decorator}\nexport class {name} {{\n"
    ts_code += "\n\n".join(typescript_fields)
    ts_code += "\n}"

    return ts_code

def camel_to_kebab(s):
    result = ''.join(['-' + i.lower() if i.isupper() else i for i in s]).lstrip('-')
    return result.replace('-input', '') if s.endswith("Input") else result

def main(input_filepath, output_dir):
    with open(input_filepath, 'r') as f:
        data = f.read()

    with open("config.json", "r") as cf:
        config = json.load(cf)

    # Extraction précise des blocs "type" et "input" avec regex
    type_blocks = re.findall(r"(type [^{]+{[^}]+})", data)
    input_blocks = re.findall(r"(input [^{]+{[^}]+})", data)

    for block in type_blocks:
        output_code = transform_to_nestjs(block, config)
        name = block.split()[1]  # Utilisez l'index 1 pour extraire le nom après "type"
        filename = f"{camel_to_kebab(name)}.dto.ts"
        with open(os.path.join(output_dir, filename), "w") as out_f:
            out_f.write(output_code)

    for block in input_blocks:
        output_code = transform_to_nestjs(block, config, is_input=True)
        name = block.split()[1]  # Utilisez l'index 1 pour extraire le nom après "input"
        filename = f"{camel_to_kebab(name)}.input.dto.ts"
        with open(os.path.join(output_dir, filename), "w") as out_f:
            out_f.write(output_code)

if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
