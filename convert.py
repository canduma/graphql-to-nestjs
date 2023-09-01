import json
import os
import sys

def transform_to_nestjs(schema_block, config):
    block_lines = schema_block.strip().split("\n")
    name = block_lines[0].split("{")[0].strip().split()[-1]

    if name in ["Mutation", "Query", "Subscription"]:
        return ""

    fields = block_lines[1:-1]

    imports = set()
    typescript_fields = []

    for i in range(0, len(fields)):
        field_data = fields[i].strip()
        split_data = field_data.split(":")
        
        if len(split_data) != 2:
            continue
        
        field_name, field_type_raw = map(str.strip, split_data)
        nullable = field_type_raw.endswith("!")
        field_type = field_type_raw.replace("!", "").strip()

        if field_type in config['mapping']:
            ts_type = config['mapping'][field_type]['typescriptType']
            if 'import' in config['mapping'][field_type]:
                imports.add(config['mapping'][field_type]['import'])
        else:
            ts_type = field_type  # default to same type

        field_str = f'  @Field(() => {field_type}, {{ nullable: {str(nullable).lower()} }})\n'
        field_str += f'  {field_name}: {ts_type};'
        typescript_fields.append(field_str)

    import_str = "\n".join(sorted(imports))

    if name not in ["Query", "Mutation", "Subscription"]:
        decorator = "@ObjectType()"
    else:
        decorator = "@Resolver()"

    ts_code = f"{import_str}\n\n{decorator}\nexport class {name} {{\n"
    ts_code += "\n\n".join(typescript_fields)
    ts_code += "\n}"

    return ts_code

def camel_to_kebab(s):
    return ''.join(['-' + i.lower() if i.isupper() else i for i in s]).lstrip('-')


def main(input_filepath, output_dir):
    with open(input_filepath, 'r') as f:
        data = f.read()

    with open("config.json", "r") as cf:
        config = json.load(cf)

    blocks = data.split("type ")

    for block in blocks:
        if not block.strip():
            continue
        output_code = transform_to_nestjs(block, config)
        name = block.split()[0]
        if name in ["Mutation", "Query", "Subscription"]:
            continue
        filename = f"{camel_to_kebab(name)}.dto.ts"
        with open(os.path.join(output_dir, filename), "w") as out_f:
            out_f.write(output_code)

if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
