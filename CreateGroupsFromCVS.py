import pandas as pd
import requests

# GraphQL endpoint and headers
graphql_endpoint = "https://your-wiki-instance/graphql"
headers = {
    "Authorization": "Bearer YOUR_ACCESS_TOKEN",  # Don't remove the Bearer !!
    "Content-Type": "application/json"
}

# Read the group list from a CSV file
group_list = pd.read_csv('The-path-of-your-list.csv')  # Adjust the path and file format as needed

# Mutation to create a group
create_group_mutation = """
mutation CreateGroup($name: String!) {
  groups {
    create(name: $name) {
      responseResult {
        succeeded
        message
      }
    }
  }
}
"""

def create_group(group_name):
    response = requests.post(
        graphql_endpoint,
        headers=headers,
        json={
            "query": create_group_mutation,
            "variables": {"name": group_name}
        }
    )
    return response.json()

for group_name in group_list['GroupName']:  # Adjust column name if necessary
    result = create_group(group_name)
    if 'errors' in result:
        print(f"Error creating group {group_name}: {result['errors']}")
    else:
        response_result = result['data']['groups']['create']['responseResult']
        if response_result['succeeded']:
            print(f"Group created successfully: {group_name}")
        else:
            print(f"Failed to create group {group_name}: {response_result['message']}")

print("Group synchronization completed.")
