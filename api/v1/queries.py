import json
from typing import Optional


def by_id(type: str, values: str) -> str:
    return f"""
        query by_id($urn: String!) {{
            {type}(urn: $urn) {{ {values} }}
        }}
    """

def by_name(values: str) -> str:
    return f"""
        query by_name($input: AutoCompleteInput!) {{
            results: autoComplete(input: $input) {{
                __typename
                entities {{ {values} }}
            }}
        }}
    """

def by_query(values: str) -> str:
    return f"""
        query by_query($input: SearchInput!) {{
            results: search(input: $input) {{
                __typename start count total
                entities: searchResults {{ entity {{ {values} }} }}
            }}
        }}
    """

def platforms(values: str) -> str:
    return f"""
        query platforms($input: ListRecommendationsInput!) {{
            results: listRecommendations(input: $input) {{
                modules {{
                    id: moduleId
                    content {{ entity {{ {values} }} }}
                }}
            }}
        }}
    """

def add_tag() -> str:
    return """
        mutation add_tag($input: TagAssociationInput!) {
            success: addTag(input: $input)
        }
    """

def remove_tag() -> str:
    return """
        mutation remove_tag($input: TagAssociationInput!) {
            success: removeTag(input: $input)
        }
    """

def create_tag(name: str, description: Optional[str]) -> dict[str, str]:
    return {
        "entity": {
            "value": {
                "com.linkedin.metadata.snapshot.TagSnapshot": {
                    "urn": f"urn:li:tag:{name}",
                    "aspects": [{
                        "com.linkedin.tag.TagProperties": {
                            "name": name,
                            "description": description
                        }
                    }]
                }
            }
        }
    }

def delete_tag(urn: str) -> dict[str, str]:
    return {
        "entity": {
            "value": {
                "com.linkedin.metadata.snapshot.TagSnapshot": {
                    "urn": urn,
                    "aspects": [{
                        "com.linkedin.common.Status": {
                            "removed": True
                        }
                    }]
                }
            }
        }
    }
