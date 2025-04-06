import json

# Sample Marxist theory Q&A pairs
sample_data = [
    {
        "conversation": [
            {"from": "human", "value": "What is the Communist Manifesto?"},
            {"from": "assistant", "value": "The Communist Manifesto is a political pamphlet written by Karl Marx and Friedrich Engels in 1848, outlining the core principles of communism and the Communist League's program."}
        ]
    },
    {
        "conversation": [
            {"from": "human", "value": "What does Marx mean by 'class struggle'?"},
            {"from": "assistant", "value": "For Marx, class struggle refers to the conflict between social classes, particularly between the bourgeoisie (capitalist class) and the proletariat (working class), which he saw as the driving force of historical development and social change."}
        ]
    },
    {
        "conversation": [
            {"from": "human", "value": "What is the labor theory of value?"},
            {"from": "assistant", "value": "The labor theory of value is an economic concept developed by Marx which states that the value of a commodity is determined by the socially necessary labor time required to produce it."}
        ]
    },
    {
        "conversation": [
            {"from": "human", "value": "What is 'surplus value' according to Marx?"},
            {"from": "assistant", "value": "Surplus value is a concept in Marxian economics representing the difference between the value created by a worker's labor and the wages paid to them, which is appropriated by the capitalist as profit."}
        ]
    },
    {
        "conversation": [
            {"from": "human", "value": "What is the dictatorship of the proletariat?"},
            {"from": "assistant", "value": "The dictatorship of the proletariat refers to a transitional state in which the working class holds political power, with the aim of transitioning from capitalism to socialism and eventually communism."}
        ]
    },
    {
        "conversation": [
            {"from": "human", "value": "How does Marx define capitalism?"},
            {"from": "assistant", "value": "Marx defines capitalism as an economic system based on private ownership of the means of production, wage labor, and the production of commodities for profit, characterized by class division between capitalists and workers."}
        ]
    },
    {
        "conversation": [
            {"from": "human", "value": "What is historical materialism?"},
            {"from": "assistant", "value": "Historical materialism is Marx's theory of history that emphasizes material conditions and economic factors as the primary influences on social structure and development, rather than ideas or consciousness."}
        ]
    },
    {
        "conversation": [
            {"from": "human", "value": "What is commodity fetishism?"},
            {"from": "assistant", "value": "Commodity fetishism is a concept introduced by Marx in Das Kapital, describing how social relationships in capitalist societies are perceived as economic relationships between commodities, obscuring the actual social relations between people."}
        ]
    },
    {
        "conversation": [
            {"from": "human", "value": "What did Marx mean by 'alienation'?"},
            {"from": "assistant", "value": "Alienation in Marx's theory refers to the estrangement of workers from their labor, the products they create, their human nature, and from other people, as a result of capitalist production methods."}
        ]
    },
    {
        "conversation": [
            {"from": "human", "value": "What is the base and superstructure in Marxist theory?"},
            {"from": "assistant", "value": "In Marxist theory, the base consists of the economic relations and means of production, while the superstructure includes institutions, political structures, legal systems, and ideologies that emerge from and reinforce the economic base."}
        ]
    }
]

# Save to file
with open("marx_sample.jsonl", "w", encoding="utf-8") as f:
    for entry in sample_data:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")

print(f"Created sample dataset with {len(sample_data)} Q&A pairs. Saved to marx_sample.jsonl") 