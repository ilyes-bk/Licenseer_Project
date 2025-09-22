import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
from matplotlib.patches import FancyBboxPatch, ConnectionPatch
import networkx as nx

def create_license_compatibility_graph():
    """
    Create a sample knowledge graph visualization showing:
    - 6 dependencies (3 per license)
    - 2 licenses (MIT and GPL-3.0)
    - License terms and compatibility relationships
    """
    
    # Create figure with subplots
    fig = plt.figure(figsize=(16, 12))
    
    # Main graph area
    ax_main = plt.subplot2grid((3, 3), (0, 0), colspan=3, rowspan=2)
    ax_main.set_xlim(0, 10)
    ax_main.set_ylim(0, 8)
    ax_main.axis('off')
    
    # License terms area
    ax_terms = plt.subplot2grid((3, 3), (2, 0), colspan=3)
    ax_terms.axis('off')
    
    # Define colors
    colors = {
        'MIT': '#2E8B57',      # Sea Green
        'GPL-3.0': '#DC143C',  # Crimson
        'dependency': '#4682B4', # Steel Blue
        'compatible': '#32CD32', # Lime Green
        'incompatible': '#FF6347', # Tomato
        'neutral': '#DDA0DD'    # Plum
    }
    
    # License nodes
    licenses = {
        'MIT': {'pos': (2, 6), 'color': colors['MIT'], 'size': 800},
        'GPL-3.0': {'pos': (8, 6), 'color': colors['GPL-3.0'], 'size': 800}
    }
    
    # Dependencies
    dependencies = {
        'requests': {'license': 'MIT', 'pos': (1, 4), 'color': colors['dependency']},
        'numpy': {'license': 'MIT', 'pos': (2, 4), 'color': colors['dependency']},
        'pandas': {'license': 'MIT', 'pos': (3, 4), 'color': colors['dependency']},
        'tensorflow': {'license': 'GPL-3.0', 'pos': (7, 4), 'color': colors['dependency']},
        'pytorch': {'license': 'GPL-3.0', 'pos': (8, 4), 'color': colors['dependency']},
        'scikit-learn': {'license': 'GPL-3.0', 'pos': (9, 4), 'color': colors['dependency']}
    }
    
    # Draw license nodes
    for license_name, info in licenses.items():
        circle = plt.Circle(info['pos'], 0.8, color=info['color'], alpha=0.8, zorder=3)
        ax_main.add_patch(circle)
        ax_main.text(info['pos'][0], info['pos'][1], license_name, 
                    ha='center', va='center', fontsize=12, fontweight='bold', 
                    color='white', zorder=4)
    
    # Draw dependency nodes
    for dep_name, info in dependencies.items():
        rect = FancyBboxPatch((info['pos'][0]-0.4, info['pos'][1]-0.3), 
                            0.8, 0.6, boxstyle="round,pad=0.1",
                            facecolor=info['color'], alpha=0.8, zorder=3)
        ax_main.add_patch(rect)
        ax_main.text(info['pos'][0], info['pos'][1], dep_name, 
                    ha='center', va='center', fontsize=10, fontweight='bold', 
                    color='white', zorder=4)
    
    # Draw license-dependency connections
    for dep_name, info in dependencies.items():
        license_pos = licenses[info['license']]['pos']
        dep_pos = info['pos']
        
        # Connection line
        line = ConnectionPatch(license_pos, dep_pos, "data", "data",
                              arrowstyle="->", shrinkA=5, shrinkB=5,
                              mutation_scale=20, fc="gray", alpha=0.7, zorder=2)
        ax_main.add_patch(line)
    
    # Add compatibility analysis
    compatibility_text = """
    COMPATIBILITY ANALYSIS:
    
    MIT License Terms:
    • Permissive: Allows commercial use, modification, distribution
    • Compatible with: GPL-3.0 (can be combined)
    • No copyleft restrictions
    
    GPL-3.0 License Terms:
    • Copyleft: Requires derivative works to be GPL-3.0
    • Incompatible with: MIT (cannot be combined in same project)
    • Strong copyleft restrictions
    """
    
    ax_terms.text(0.05, 0.95, compatibility_text, transform=ax_terms.transAxes,
                 fontsize=11, verticalalignment='top', fontfamily='monospace',
                 bbox=dict(boxstyle="round,pad=0.5", facecolor='lightgray', alpha=0.8))
    
    # Add legend
    legend_elements = [
        mpatches.Patch(color=colors['MIT'], label='MIT License'),
        mpatches.Patch(color=colors['GPL-3.0'], label='GPL-3.0 License'),
        mpatches.Patch(color=colors['dependency'], label='Dependencies'),
        mpatches.Patch(color=colors['compatible'], label='Compatible'),
        mpatches.Patch(color=colors['incompatible'], label='Incompatible')
    ]
    
    ax_main.legend(handles=legend_elements, loc='upper right', 
                  bbox_to_anchor=(0.98, 0.98), fontsize=10)
    
    # Add title
    ax_main.text(5, 7.5, 'LARK Knowledge Graph: License Compatibility Analysis', 
                ha='center', va='center', fontsize=16, fontweight='bold')
    
    # Add subtitle
    ax_main.text(5, 7, 'Sample: 6 Dependencies, 2 Licenses, Compatibility Terms', 
                ha='center', va='center', fontsize=12, style='italic')
    
    # Add compatibility matrix
    matrix_text = """
    COMPATIBILITY MATRIX:
    
    License Pair    | Compatibility | Reason
    ----------------|---------------|------------------
    MIT + MIT       | ✓ Compatible  | Same permissive terms
    MIT + GPL-3.0   | ✗ Incompatible| GPL-3.0 requires copyleft
    GPL-3.0 + GPL-3.0| ✓ Compatible | Same copyleft terms
    """
    
    ax_terms.text(0.05, 0.45, matrix_text, transform=ax_terms.transAxes,
                 fontsize=10, verticalalignment='top', fontfamily='monospace',
                 bbox=dict(boxstyle="round,pad=0.5", facecolor='lightblue', alpha=0.8))
    
    plt.tight_layout()
    return fig

def create_neo4j_style_graph():
    """
    Create a Neo4j-style graph visualization for the research paper
    """
    fig, ax = plt.subplots(figsize=(14, 10))
    
    # Create a NetworkX graph
    G = nx.Graph()
    
    # Add nodes
    G.add_node('MIT', node_type='license', color='#2E8B57')
    G.add_node('GPL-3.0', node_type='license', color='#DC143C')
    
    # Add dependencies
    dependencies = ['requests', 'numpy', 'pandas', 'tensorflow', 'pytorch', 'scikit-learn']
    for dep in dependencies:
        G.add_node(dep, node_type='dependency', color='#4682B4')
    
    # Add edges (license-dependency relationships)
    G.add_edge('MIT', 'requests')
    G.add_edge('MIT', 'numpy')
    G.add_edge('MIT', 'pandas')
    G.add_edge('GPL-3.0', 'tensorflow')
    G.add_edge('GPL-3.0', 'pytorch')
    G.add_edge('GPL-3.0', 'scikit-learn')
    
    # Add compatibility edges
    G.add_edge('MIT', 'GPL-3.0', relationship='incompatible', color='#FF6347')
    
    # Position nodes
    pos = {
        'MIT': (2, 8),
        'GPL-3.0': (8, 8),
        'requests': (1, 6),
        'numpy': (2, 6),
        'pandas': (3, 6),
        'tensorflow': (7, 6),
        'pytorch': (8, 6),
        'scikit-learn': (9, 6)
    }
    
    # Draw nodes
    for node in G.nodes():
        if G.nodes[node]['node_type'] == 'license':
            nx.draw_networkx_nodes(G, pos, nodelist=[node], 
                                 node_color=G.nodes[node]['color'],
                                 node_size=1500, alpha=0.8, ax=ax)
        else:
            nx.draw_networkx_nodes(G, pos, nodelist=[node], 
                                 node_color=G.nodes[node]['color'],
                                 node_size=1000, alpha=0.8, ax=ax)
    
    # Draw edges
    nx.draw_networkx_edges(G, pos, edge_color='gray', alpha=0.6, ax=ax)
    
    # Draw labels
    nx.draw_networkx_labels(G, pos, font_size=10, font_weight='bold', ax=ax)
    
    # Add title
    ax.set_title('LARK Knowledge Graph: Neo4j Database Structure\nLicense-Dependency Relationships and Compatibility Analysis', 
                fontsize=14, fontweight='bold', pad=20)
    
    # Add legend
    legend_elements = [
        mpatches.Patch(color='#2E8B57', label='MIT License'),
        mpatches.Patch(color='#DC143C', label='GPL-3.0 License'),
        mpatches.Patch(color='#4682B4', label='Dependencies'),
        mpatches.Patch(color='#FF6347', label='Incompatible Relationship')
    ]
    
    ax.legend(handles=legend_elements, loc='upper left', fontsize=10)
    
    ax.axis('off')
    plt.tight_layout()
    return fig

def main():
    """
    Generate both graph visualizations for the research paper
    """
    print("🎯 Generating LARK Knowledge Graph Visualizations...")
    
    # Create the main compatibility graph
    fig1 = create_license_compatibility_graph()
    fig1.savefig('images/lark_license_compatibility_graph.png', 
                dpi=300, bbox_inches='tight', facecolor='white')
    print("✅ Saved: lark_license_compatibility_graph.png")
    
    # Create the Neo4j-style graph
    fig2 = create_neo4j_style_graph()
    fig2.savefig('images/lark_neo4j_knowledge_graph.png', 
                dpi=300, bbox_inches='tight', facecolor='white')
    print("✅ Saved: lark_neo4j_knowledge_graph.png")
    
    print("\n🎉 Graph visualizations created successfully!")
    print("📊 Perfect for your research paper to demonstrate LARK's knowledge graph!")
    
    # Show the graphs
    plt.show()

if __name__ == "__main__":
    main()
