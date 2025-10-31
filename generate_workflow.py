import json
import uuid

def generate_n8n_workflow():
    """Generate n8n workflow JSON for the Bible Verse Agent"""

    workflow = {
        "active": False,
        "category": "utilities",
        "description": "A workflow that provides Bible verses with AI reflections",
        "id": str(uuid.uuid4())[:16],  # Generate a short unique ID
        "long_description": """
      You are a helpful Bible verse assistant that provides meaningful Bible verses with AI-generated reflections.

      Your primary function is to help users find relevant Bible verses for specific topics or situations. When responding:

      - Always extract the main topic from the user's query (e.g., "faith", "love", "forgiveness")
      - Provide a relevant Bible verse from the specified topic
      - Include an AI-generated reflection to help users understand the verse's meaning
      - Keep responses concise but spiritually meaningful
      - If the user asks for daily verses, provide a random verse with reflection
      - Support both Old and New Testament verses

      Use the bibleVerseTool to fetch verses and generate reflections.
""",
        "name": "bible_verse_agent",
        "nodes": [
            {
                "id": "bible_verse_agent",
                "name": "Bible Verse Agent",
                "parameters": {},
                "position": [
                    816,
                    -112
                ],
                "type": "a2a/mastra-a2a-node",
                "typeVersion": 1,
                "url": "https://hng4-production.up.railway.app/a2a"
            }
        ],
        "pinData": {},
        "settings": {
            "executionOrder": "v1"
        },
        "short_description": "Provides Bible verses with AI reflections"
    }

    return workflow

if __name__ == "__main__":
    workflow = generate_n8n_workflow()
    print(json.dumps(workflow, indent=2))

    # Save to file
    with open("bible_verse_workflow.json", "w") as f:
        json.dump(workflow, f, indent=2)

    print("\nWorkflow saved to bible_verse_workflow.json")
