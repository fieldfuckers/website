#!/usr/bin/env python3
"""
Retrieve Steam group members and their details.

This script:
1. Fetches the XML member list from the Steam community group
2. Parses the steamID64 values for all members
3. Retrieves player summaries from the Steam API for those members
"""

import os
import sys
import requests
import xml.etree.ElementTree as ET
from typing import List, Dict, Any


STEAM_GROUP_URL = "https://steamcommunity.com/groups/fieldfuckers/memberslistxml/?xml=1"
STEAM_API_URL = "https://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002/"


def fetch_group_xml() -> str:
    """Fetch the XML member list from the Steam community group."""
    try:
        response = requests.get(STEAM_GROUP_URL, timeout=10)
        response.raise_for_status()
        return response.text
    except requests.exceptions.RequestException as e:
        print(f"Error fetching group XML: {e}", file=sys.stderr)
        sys.exit(1)


def parse_steam_ids(xml_content: str) -> List[str]:
    """Parse steamID64 values from the XML content."""
    try:
        root = ET.fromstring(xml_content)
        
        # Find all steamID64 elements within the members section
        steam_ids = []
        for steam_id_elem in root.findall(".//members/steamID64"):
            if steam_id_elem.text:
                steam_ids.append(steam_id_elem.text.strip())
        
        return steam_ids
    except ET.ParseError as e:
        print(f"Error parsing XML: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error extracting steam IDs: {e}", file=sys.stderr)
        sys.exit(1)


def get_player_summaries(steam_ids: List[str], api_key: str) -> Dict[str, Any]:
    """Retrieve player summaries from the Steam API."""
    if not steam_ids:
        print("No steam IDs to query", file=sys.stderr)
        return {}
    
    # Steam API accepts comma-separated steam IDs
    steamids_param = ",".join(steam_ids)
    
    params = {
        "key": api_key,
        "steamids": steamids_param
    }
    
    try:
        response = requests.get(STEAM_API_URL, params=params, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching player summaries: {e}", file=sys.stderr)
        sys.exit(1)


def main():
    """Main function to orchestrate the script."""
    # Get API key from environment variable
    api_key = os.getenv("STEAM_API_KEY")
    if not api_key:
        print("Error: STEAM_API_KEY environment variable is not set", file=sys.stderr)
        sys.exit(1)
    
    # Step 1: Fetch the group XML
    print("Fetching group member list...", file=sys.stderr)
    xml_content = fetch_group_xml()
    
    # Step 2: Parse steam IDs
    print("Parsing steam IDs...", file=sys.stderr)
    steam_ids = parse_steam_ids(xml_content)
    print(f"Found {len(steam_ids)} members", file=sys.stderr)

    # Step 3: Fetch player summaries
    print("Fetching player summaries...", file=sys.stderr)
    player_data = get_player_summaries(steam_ids, api_key)

    # Step 4: Sort players by steamid (lowest to highest) and filter to only required properties
    import json
    filtered_data = {"response": {"players": []}}

    if "response" in player_data and "players" in player_data["response"]:
        players = player_data["response"]["players"]
        # Sort by steamid (lowest to highest)
        players.sort(key=lambda p: int(p.get("steamid", "0")))

        # Filter to only include required properties
        required_properties = ["steamid", "personaname", "profileurl", "avatarfull"]
        for player in players:
            filtered_player = {
                key: player.get(key)
                for key in required_properties
                if key in player
            }
            filtered_data["response"]["players"].append(filtered_player)

    # Output the JSON result
    print(json.dumps(filtered_data, indent=2))


if __name__ == "__main__":
    main()
