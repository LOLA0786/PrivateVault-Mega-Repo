import yaml
import logging

def load_compliance_map(file_path='compliance_map.yaml'):
    with open(file_path, 'r') as f:
        return yaml.safe_load(f)

def map_event_to_controls(event_type, tool_name, metadata):
    compliance_map = load_compliance_map()
    tags = []
    for control, data in compliance_map['controls'].items():
        if event_type in data['evidence'] or tool_name in data['evidence']:
            tags.append(control)
    logging.info(f"Mapped tags for {event_type}: {tags}")
    return tags

if __name__ == "__main__":
    # Test
    tags = map_event_to_controls('tool_auth', 'file_system_read', {})
    print(tags)
