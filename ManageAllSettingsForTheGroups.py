import pandas as pd
import requests
import re

# Replace with your actual GraphQL endpoint and headers if needed
graphql_endpoint = "https://your-wiki-instance/graphql"
headers = {
    "Authorization": "Bearer YOUR_ACCESS_TOKEN",  # Don't remove the Bearer !!
    "Content-Type": "application/json"
}

# Function to create the custom path
def create_custom_path(name):
    name = re.sub(r'[.\s]', '-', name)  # Replace dots and spaces with dashes
    custom_path = ''.join([f'[{c.lower()}{c.upper()}]' for c in name])
    return custom_path

# Mutation to fetch all groups
fetch_groups_query = """
query {
  groups {
    list {
      id
      name
    }
  }
}
"""

# Fetch the groups and store their IDs and names
response = requests.post(graphql_endpoint, headers=headers, json={"query": fetch_groups_query})
groups_data = response.json()

if 'errors' in groups_data:
    print("Error fetching groups:", groups_data['errors'])
else:
    groups = groups_data['data']['groups']['list']
    group_dict = {group['name']: group['id'] for group in groups}

    print("Fetched groups:", group_dict)

# Read the group list from a CSV file and debug the columns
csv_file_path = 'The-path-of-your-list.csv'
group_list = pd.read_csv(csv_file_path)

# Print column names to debug
print("CSV Columns:", group_list.columns)

# Mutation to update a group
update_group_mutation = """
mutation UpdateGroup($id: Int!, $name: String!, $redirectOnLogin: String!, $permissions: [String!]!, $pageRules: [PageRuleInput!]!) {
  groups {
    update(id: $id, name: $name, redirectOnLogin: $redirectOnLogin, permissions: $permissions, pageRules: $pageRules) {
      responseResult {
        succeeded
        message
      }
    }
  }
}
"""

# Iterate over the group list and update each group
for index, row in group_list.iterrows():
    try:
        group_name = row['GroupName']  # Change 'name' to the correct column name
        group_id = group_dict.get(group_name)  # Get the group ID from the fetched groups

        if group_id is not None:
            custom_path = create_custom_path(group_name)
            
            variables = {
                "id": group_id,
                "name": group_name,
                "redirectOnLogin": "/home",
                "permissions": [
                    "read:pages",
                    "read:source",
                    "read:history",
                    "read:assets",
                    "read:comments",
                    "write:comments",
                    "write:pages",
                    "write:assets",
                    "write:scripts",
                    "write:styles",
                    "delete:pages",
                    "manage:pages",
                    "manage:assets"
                ],
                "pageRules": [
                    {
                        "id": "rule1",
                        "deny": False,
                        "match": "REGEX",
                        "roles": [
                            "read:pages",
                            "read:source",
                            "read:history",
                            "read:assets",
                            "read:comments",
                            "write:comments",
                            "write:pages",
                            "write:assets",
                            "write:scripts",
                            "write:styles",
                            "delete:pages",
                            "manage:pages",
                            "manage:assets",
                        ],
                        "path": custom_path,
                        "locales": [
                            
                        ]
                    },
                    {
                        "id": "rule2",
                        "deny": False,
                        "match": "EXACT",
                        "roles": [
                            "read:pages",
                            "read:source",
                            "read:history",
                            "read:assets",
                            "read:comments",
                            "write:comments"
                        ],
                        "path": "home",
                        "locales": [
                            
                        ]
                    },
                    {
                        "id": "rule3",
                        "deny": False,
                        "match": "START",
                        "roles": [
                            "read:assets"
                        ],
                        "path": "",
                        "locales": [
                            
                        ]
                    }
                ]
            }

            response = requests.post(graphql_endpoint, headers=headers, json={"query": update_group_mutation, "variables": variables})
            response_data = response.json()

            if response_data.get("errors"):
                print(f"Error updating group {group_name}: {response_data['errors']}")
            else:
                print(f"Successfully updated group {group_name}")
        else:
            print(f"Group {group_name} not found")

    except KeyError as e:
        print(f"Error with row {index}: Column '{e}' not found in the CSV")

print("Group update completed.")
