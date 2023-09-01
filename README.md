# GraphQL to NestJS DTO Converter

This utility script converts a GraphQL schema into NestJS DTOs. It reads the schema file and generates one `.dto.ts` file for each type in the schema. The script uses a configuration file `config.json` to map GraphQL types to TypeScript types and can automatically include necessary imports.

## Setup

1. Clone the repository:
```
git clone [repository_link]
```

2. Navigate to the directory:
```
cd [directory_name]
```

3. Ensure you have Python 3 installed.

## Configuration

Before running the script, you need to set up the `config.json` file, which provides the mapping between GraphQL and TypeScript types. An example configuration `config.example.json` is provided in the repository.

The configuration file has two main sections:
- `mapping`: Maps GraphQL types to TypeScript types, and optionally specifies an import statement.
- `native_types`: Lists GraphQL types that are native to NestJS GraphQL (like ID, Int, Boolean, etc.)

Here's a sample configuration:

```json
{
    "mapping": {
        "User": {
            "convert": "User2",
            "import": "import { User } from './post.entity';",
            "typescriptType": "User"
        },
        ...
    },
    "native_types": ["ID", "Int", "Boolean", "Float", "String"]
}
```

## Running the Script

To run the script, use the following command:

```
python3 convert.py <input_schema_filepath> <output_directory>
```

For example:

```
python3 convert.py test.graphql output
```

After execution, you should see multiple `.dto.ts` files in the specified output directory, one for each type in the GraphQL schema.

## Note

This script is designed for basic schema conversions. For complex schemas with various custom scalars, enums, etc., manual adjustments might be needed.
