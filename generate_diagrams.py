#!/usr/bin/env python3
import matplotlib.pyplot as plt
import networkx as nx
from matplotlib.patches import Rectangle, FancyBboxPatch
import os

# Create output directory if it doesn't exist
if not os.path.exists('images'):
    os.makedirs('images')

# DIAGRAM 1: Knowledge Graph Construction
def create_knowledge_graph():
    plt.figure(figsize=(8, 5))
    
    # Create graph
    G = nx.DiGraph()
    
    # Add nodes
    G.add_node("requests", pos=(1, 2))
    G.add_node("MIT", pos=(3, 2))
    G.add_node("GPL", pos=(5, 2))
    G.add_node("Attribution", pos=(4, 0.5))
    
    # Add edges
    G.add_edge("requests", "MIT", style="dashed", label="HAS_LICENSE")
    G.add_edge("MIT", "GPL", label="COMPATIBLE_WITH")
    G.add_edge("MIT", "Attribution", label="REQUIRES")
    G.add_edge("GPL", "Attribution", label="COMPATIBLE_WITH")
    
    # Get positions
    pos = nx.get_node_attributes(G, 'pos')
    
    # Draw the nodes
    nx.draw_networkx_nodes(G, pos, 
                          nodelist=["requests"],
                          node_color="white",
                          edgecolors="black",
                          node_size=2000)
    
    nx.draw_networkx_nodes(G, pos, 
                          nodelist=["MIT"],
                          node_color="lightblue",
                          edgecolors="black",
                          node_size=2000)
    
    nx.draw_networkx_nodes(G, pos, 
                          nodelist=["GPL"],
                          node_color="lightcoral",
                          edgecolors="black",
                          node_size=2000)
    
    nx.draw_networkx_nodes(G, pos, 
                          nodelist=["Attribution"],
                          node_color="lightgreen",
                          edgecolors="black",
                          node_size=2000)
    
    # Draw node labels
    nx.draw_networkx_labels(G, pos, font_size=12, font_weight="bold")
    
    # Draw edges
    for edge in G.edges(data=True):
        start, end = edge[0], edge[1]
        style = edge[2].get('style', 'solid')
        
        if style == 'dashed':
            nx.draw_networkx_edges(G, pos, edgelist=[(start, end)], 
                                  style='dashed', arrows=True,
                                  arrowstyle='->', arrowsize=20,
                                  width=1.5)
        else:
            nx.draw_networkx_edges(G, pos, edgelist=[(start, end)], 
                                  arrows=True, arrowstyle='->',
                                  arrowsize=20, width=1.5)
    
    # Draw edge labels
    edge_labels = {(u, v): d.get('label', '') for u, v, d in G.edges(data=True)}
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=10)
    
    plt.axis('off')
    plt.tight_layout()
    plt.savefig('images/knowledge_graph.png', dpi=300, bbox_inches='tight', transparent=True)
    plt.close()
    print("Knowledge Graph image saved as 'images/knowledge_graph.png'")

# DIAGRAM 2: LLM Parser Flow
def create_llm_parser_flow():
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Box heights and parameters
    box_width = 7
    box_height = 1.5
    y_spacing = 2.5
    
    # Create the boxes
    box1 = FancyBboxPatch((1, 7), box_width, box_height, 
                          boxstyle=f"round,pad=0.3,rounding_size=0.2",
                          ec="black", fc="lightblue", lw=2)
    
    box2 = FancyBboxPatch((1, 7-y_spacing), box_width, box_height, 
                          boxstyle=f"round,pad=0.3,rounding_size=0.2",
                          ec="black", fc="lightpink", lw=2)
    
    box3 = FancyBboxPatch((1, 7-2*y_spacing), box_width, box_height, 
                          boxstyle=f"round,pad=0.3,rounding_size=0.2",
                          ec="black", fc="lightgreen", lw=2)
    
    # Add boxes to the plot
    ax.add_patch(box1)
    ax.add_patch(box2)
    ax.add_patch(box3)
    
    # Add text to boxes
    ax.text(1+box_width/2, 7+box_height/2, "Custom License Text", 
            ha='center', va='center', fontsize=14)
    
    ax.text(1+box_width/2, 7-y_spacing+box_height/2, "LLM Parser (GPT-4)", 
            ha='center', va='center', fontsize=14)
    
    ax.text(1+box_width/2, 7-2*y_spacing+box_height/2, "Structured JSON Output", 
            ha='center', va='center', fontsize=14)
    
    # Add arrows
    arrow_props = dict(arrowstyle='->', lw=2, color='black')
    ax.annotate('', xy=(1+box_width/2, 7-y_spacing+box_height),
                xytext=(1+box_width/2, 7),
                arrowprops=arrow_props)
    
    ax.annotate('', xy=(1+box_width/2, 7-2*y_spacing+box_height),
                xytext=(1+box_width/2, 7-y_spacing),
                arrowprops=arrow_props)
    
    # Add explanatory text
    extract_text = "Extracts:\n• Obligations (MUST)\n• Prohibitions (CANNOT)\n• Permissions (CAN)\n• Version clauses"
    ax.text(1+box_width+1, 7-y_spacing+box_height/2, extract_text, 
            ha='left', va='center', fontsize=12)
    
    example_text = "Example:"
    ax.text(1+box_width+1, 7-2*y_spacing+box_height/2, example_text, 
            ha='left', va='center', fontsize=12)
    
    # Set axes limits
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 9)
    
    # Remove axes
    ax.axis('off')
    
    plt.tight_layout()
    plt.savefig('images/llm_parser_flow.png', dpi=300, bbox_inches='tight', transparent=True)
    plt.close()
    print("LLM Parser Flow image saved as 'images/llm_parser_flow.png'")

# Generate both diagrams
if __name__ == "__main__":
    create_knowledge_graph()
    create_llm_parser_flow()
    print("All diagrams generated successfully!") 