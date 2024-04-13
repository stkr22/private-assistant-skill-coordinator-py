# Private Assistant Skill Coordinator

## Overview

The Coordinator is an essential component of a Modular Private Assistant ecosystem, designed to work in tandem with edge device clients and skill-based services over MQTT. It acts as the central orchestrator, efficiently managing communication and decision-making processes to determine the most relevant skill for a given user command.

## How It Works

Upon receiving a spoken command from an edge device, the client sends this text to a central MQTT server. Various skills, each listening to specific MQTT topics, evaluate the command's relevance to their functionality and respond with a certainty score. The Coordinator collects these scores and directs the command to the skill with the highest certainty, ensuring that the assistant responds accurately and contextually to user requests.

## Features

- **Centralized Orchestration**: Manages the flow of messages between the client and skills, ensuring seamless operation.
- **Dynamic Skill Selection**: Dynamically selects the most relevant skill based on certainty scores, improving the accuracy and relevance of responses.
- **MQTT Integration**: Utilizes MQTT for efficient, lightweight communication across the assistant's components, facilitating scalability and flexibility.
- **Modular Design**: Supports a modular ecosystem, allowing for the easy addition of new skills and functionalities.

## Getting Started

This section should include basic setup instructions, such as installing MQTT, setting up the Coordinator, and linking it with other components of the assistant.

## Contribution

We welcome contributions! Whether you're looking to fix bugs, add new features, or improve documentation, please feel free to make a pull request.
