import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import Circle
import numpy as np

def create_simple_neo4j_graph():
    """
    Create a simple, clean Neo4j-style knowledge graph
    """
    fig, ax = plt.subplots(figsize=(12, 8))
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 8)
    ax.axis('off')
    
    # Simple colors
    colors = {
        'license': '#68BC00',      # Neo4j green
        'dependency': '#FF6B35',   # Neo4j orange
        'incompatible': '#E74C3C'  # Red for incompatible
    }
    
    # Simple node positions
    nodes = {
        'MIT': {'pos': (2, 6), 'color': colors['license']},
        'GPL-3.0': {'pos': (10, 6), 'color': colors['license']},
        'requests': {'pos': (1, 3), 'color': colors['dependency']},
        'numpy': {'pos': (2, 3), 'color': colors['dependency']},
        'pandas': {'pos': (3, 3), 'color': colors['dependency']},
        'tensorflow': {'pos': (9, 3), 'color': colors['dependency']},
        'pytorch': {'pos': (10, 3), 'color': colors['dependency']},
        'scikit-learn': {'pos': (11, 3), 'color': colors['dependency']},
        
        # License terms
        'MIT_terms': {'pos': (2, 1), 'color': '#5DADE2', 'terms': ['Permissive', 'No Copyleft', 'Commercial Use OK']},
        'GPL_terms': {'pos': (10, 1), 'color': '#5DADE2', 'terms': ['Copyleft', 'Derivative Works', 'Commercial Restricted']}
    }
    
    # Draw nodes
    for node_name, node_data in nodes.items():
        pos = node_data['pos']
        color = node_data['color']
        
        # Draw circle
        circle = Circle(pos, 0.4, facecolor=color, edgecolor='black', linewidth=2)
        ax.add_patch(circle)
        
        # Draw label
        if 'terms' in node_data:
            # For term nodes, show the terms
            terms = node_data['terms']
            ax.text(pos[0], pos[1], '\n'.join(terms), ha='center', va='center',
                   fontsize=8, fontweight='bold', color='white')
        else:
            # For regular nodes, show the name
            ax.text(pos[0], pos[1], node_name, ha='center', va='center',
                   fontsize=10, fontweight='bold', color='white')
    
    # Draw relationships
    relationships = [
        # License to dependencies
        ('MIT', 'requests'),
        ('MIT', 'numpy'),
        ('MIT', 'pandas'),
        ('GPL-3.0', 'tensorflow'),
        ('GPL-3.0', 'pytorch'),
        ('GPL-3.0', 'scikit-learn'),
        
        # License to terms
        ('MIT', 'MIT_terms'),
        ('GPL-3.0', 'GPL_terms'),
        
        # Incompatibility
        ('MIT', 'GPL-3.0')
    ]
    
    for start, end in relationships:
        start_pos = nodes[start]['pos']
        end_pos = nodes[end]['pos']
        
        if start == 'MIT' and end == 'GPL-3.0':
            # Incompatible relationship - red dashed line
            ax.plot([start_pos[0], end_pos[0]], [start_pos[1], end_pos[1]], 
                   color=colors['incompatible'], linewidth=3, linestyle='--', alpha=0.8)
            ax.text((start_pos[0] + end_pos[0])/2, (start_pos[1] + end_pos[1])/2 + 0.5,
                   'INCOMPATIBLE', ha='center', va='center', fontsize=9, fontweight='bold',
                   color=colors['incompatible'])
        else:
            # Regular relationship - gray line
            ax.plot([start_pos[0], end_pos[0]], [start_pos[1], end_pos[1]], 
                   color='gray', linewidth=2, alpha=0.7)
    
    # Add title
    ax.text(6, 7.5, 'LARK Knowledge Graph', ha='center', va='center', 
           fontsize=16, fontweight='bold')
    
    # Add simple legend
    legend_elements = [
        mpatches.Patch(color=colors['license'], label='License'),
        mpatches.Patch(color=colors['dependency'], label='Dependency'),
        mpatches.Patch(color='#5DADE2', label='License Terms'),
        mpatches.Patch(color=colors['incompatible'], label='Incompatible')
    ]
    
    ax.legend(handles=legend_elements, loc='upper right', fontsize=10)
    
    # Add simple info
    ax.text(6, 0.5, 'MIT + GPL-3.0 = Incompatible (Copyleft vs Permissive)', 
           ha='center', va='center', fontsize=11, style='italic',
           bbox=dict(boxstyle="round,pad=0.3", facecolor='lightgray', alpha=0.8))
    
    plt.tight_layout()
    return fig

def main():
    """
    Generate simple Neo4j-style knowledge graph
    """
    print("🎯 Generating Simple Neo4j Knowledge Graph...")
    
    # Create simple graph
    fig = create_simple_neo4j_graph()
    fig.savefig('images/lark_simple_neo4j_graph.png', 
                dpi=300, bbox_inches='tight', facecolor='white')
    print("✅ Saved: lark_simple_neo4j_graph.png")
    
    print("\n🎉 Simple Neo4j graph created successfully!")
    print("📊 Clean and simple - perfect for your research paper!")
    
    plt.show()

if __name__ == "__main__":
    main()
