from pydantic import BaseModel, Field


class GeneratedFile(BaseModel):
    project_name: str = Field(description="Name of the project being created")
    file_name: str = Field(
        description="Name of the generated Python file"
    )

    file_content: str = Field(
        description="Complete code for the file"
    )

class State(BaseModel):
    user_input: str
    generated_file: GeneratedFile | None = None