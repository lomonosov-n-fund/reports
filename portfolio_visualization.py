#!/usr/bin/env python3
"""
Portfolio Visualization Script

Creates a hierarchical donut chart to visualize crypto portfolio allocation:
- 70% Native cryptocurrencies (BTC, ETH, SOL, etc.)
- 30% Stablecoins (USDT, USDC, DAI, etc.)

Each class segment is subdivided into individual crypto weights based on market capitalization.
"""

import json
from pathlib import Path

import click
import matplotlib.pyplot as plt
import numpy as np
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Portfolio allocation constants
NATIVE_CRYPTO_ALLOCATION = 0.70
STABLECOIN_ALLOCATION = 0.30

# Color schemes
NATIVE_COLORS = ['#FF6B35', '#FF8C42', '#FFA726', '#FFB74D', '#FFCC80']
STABLECOIN_COLORS = ['#26A17B', '#4CAF50', '#66BB6A']

# Default asset allocation data (in billions USD)
DEFAULT_DATA = {
    'native_cryptocurrencies': {
        'BTC': 1200,
        'ETH': 450,
        'SOL': 180,
        'ADA': 45,
        'DOT': 35,
    },
    'stablecoins': {
        'USDT': 95,
        'USDC': 32,
        'DAI': 5,
    }
}


def load_asset_allocation():
    """Load asset allocation data from JSON file."""
    try:
        with open('asset_allocation.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print("Warning: asset_allocation.json not found. Using default data.")
        return DEFAULT_DATA


def calculate_weights(market_caps):
    """Calculate percentage weights based on market capitalization."""
    total_market_cap = sum(market_caps.values())
    return {crypto: (market_cap / total_market_cap) * 100 
            for crypto, market_cap in market_caps.items()}


def create_hierarchical_donut_chart():
    """Create a nested chart: outer donut with individual coins, inner pie with 70-30 division."""
    asset_data = load_asset_allocation()
    
    # Calculate weights within each class
    native_weights = calculate_weights(asset_data['native_cryptocurrencies'])
    stablecoin_weights = calculate_weights(asset_data['stablecoins'])
    
    # Create figure and axis
    fig, ax = plt.subplots(figsize=(14, 10))
    
    # Prepare data for outer donut (individual coins)
    outer_labels = []
    outer_sizes = []
    outer_colors = []
    
    # Add native cryptocurrencies first (70% of portfolio)
    for crypto, weight in native_weights.items():
        portfolio_weight = (weight / 100) * NATIVE_CRYPTO_ALLOCATION * 100
        outer_labels.append(crypto)
        outer_sizes.append(portfolio_weight)
        outer_colors.append(NATIVE_COLORS[len(outer_colors) % len(NATIVE_COLORS)])
    
    # Add stablecoins second (30% of portfolio)
    for crypto, weight in stablecoin_weights.items():
        portfolio_weight = (weight / 100) * STABLECOIN_ALLOCATION * 100
        outer_labels.append(crypto)
        outer_sizes.append(portfolio_weight)
        outer_colors.append(STABLECOIN_COLORS[len(outer_colors) % len(STABLECOIN_COLORS)])
    
    # Create outer donut chart
    outer_wedges, outer_texts, outer_autotexts = ax.pie(
        outer_sizes, 
        labels=outer_labels,
        colors=outer_colors,
        autopct='%1.1f%%',
        pctdistance=0.85,
        startangle=90,
        radius=1.0,
        wedgeprops=dict(width=0.25, edgecolor='white', linewidth=2)
    )
    
    # Create inner pie chart (70-30 division)
    inner_labels = ['Нативные криптовалюты', 'Стейблкоины']
    inner_sizes = [70, 30]
    inner_colors = ['#FF6B35', '#26A17B']
    
    inner_wedges, inner_texts, inner_autotexts = ax.pie(
        inner_sizes,
        labels=None,
        colors=inner_colors,
        autopct='%1.0f%%',
        pctdistance=0.5,
        startangle=90,
        radius=0.65,
        wedgeprops=dict(edgecolor='white', linewidth=2)
    )
    
    # Style text elements
    for autotext in outer_autotexts + inner_autotexts:
        autotext.set_color('white')
        autotext.set_fontweight('bold')
        autotext.set_fontsize(16.5)
        autotext.set_bbox(dict(boxstyle="round,pad=0.3", facecolor='black', alpha=0.7))
    
    for text in outer_texts:
        text.set_fontsize(16.5)
        text.set_fontweight('bold')
    
    # Set title
    ax.set_title('Распределение криптопортфеля по классам активов\nВзвешивание по рыночной капитализации внутри класса', 
                 fontsize=16, fontweight='bold', pad=20)
    
    # Add legend
    legend_y = 1.2
    legend_spacing = 0.65
    
    # Native Cryptocurrencies legend
    ax.text(-legend_spacing, legend_y, '■', color='#FF6B35', fontsize=20, ha='center', va='center')
    ax.text(-legend_spacing + 0.05, legend_y, 'Нативные криптовалюты', 
            fontsize=14, fontweight='bold', ha='left', va='center')
    
    # Stablecoins legend
    ax.text(legend_spacing, legend_y, '■', color='#26A17B', fontsize=20, ha='center', va='center')
    ax.text(legend_spacing + 0.05, legend_y, 'Стейблкоины', 
            fontsize=14, fontweight='bold', ha='left', va='center')
    
    # Add explanatory subtitle
    ax.text(0, -1.1, "Внешнее кольцо: Веса отдельных монет | Внутренний круг: Распределение по классам активов", 
            ha='center', va='center', fontsize=11, style='italic', 
            bbox=dict(boxstyle="round,pad=0.5", facecolor='lightblue', alpha=0.3))
    
    # Set background and aspect ratio
    ax.set_facecolor('#f8f9fa')
    ax.set_aspect('equal')
    
    return fig


@click.command()
@click.option('--output-dir', default='./tmp', help='Output directory for charts')
@click.option('--format', 'output_format', default='png', 
              type=click.Choice(['png', 'svg', 'pdf']), 
              help='Output format for charts')
@click.option('--filename', default='portfolio_allocation', help='Output filename (without extension)')
@click.option('--show', is_flag=True, help='Display charts in browser')
@click.option('--verbose', is_flag=True, help='Verbose output')
def portfolio_visualization(output_dir, output_format, filename, show, verbose):
    """Generate portfolio allocation visualization chart."""
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)
    
    if verbose:
        click.echo(f"Creating portfolio visualization chart...")
        click.echo(f"Output directory: {output_path}")
        click.echo(f"Output format: {output_format}")
        click.echo(f"Output filename: {filename}")
    
    # Generate and save chart
    fig = create_hierarchical_donut_chart()
    filepath = output_path / f"{filename}.{output_format}"
    fig.savefig(str(filepath), dpi=300, bbox_inches='tight', facecolor='white')
    
    if verbose:
        click.echo(f"Saved portfolio allocation chart to: {filepath}")
    
    # Display chart if requested
    if show:
        plt.show()
    else:
        plt.close(fig)
    
    if verbose:
        click.echo("Portfolio visualization complete!")


if __name__ == '__main__':
    portfolio_visualization() 