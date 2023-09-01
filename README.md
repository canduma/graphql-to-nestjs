# GraphQL to NestJS Transformer

Transform a GraphQL schema into a NestJS entity with appropriate decorators.

## Table of Contents
- [Prerequisites](#prerequisites)
- [Configuration](#configuration)
    - [Config File Structure](#config-file-structure)
- [Usage](#usage)
- [Example](#example)

## Prerequisites

- Python 3.x

## Configuration

An example configuration file is provided named `config.example.json`. Rename this file to `config.json` and adjust it as needed.

### Config File Structure

- `mapping`: Dictionary defining how types in the GraphQL schema should be transformed for NestJS.
  - `typescriptType`: How the type should be represented in TypeScript.
  - `import`: The import statement required for this type.
  - `convert`: (Optional) If present, the GraphQL type will be replaced with this value.
  
- `native_types`: List of native types directly supported by NestJS GraphQL.

## Usage

1. Ensure Python is installed on your machine.
2. Configure `config.json` as needed.
3. Run the script:

```bash
python convert.py <input_schema_filepath> <output_filepath>
