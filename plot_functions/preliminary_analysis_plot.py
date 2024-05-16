# plot functions for different analysis plots

import numpy as np
import matplotlib.pyplot as plt




def plot_scatter_with_line(ax, scatter_x, scatter_y, scatter_properties:dict, line_x, line_y, line_properties:dict, x_label:str, y_label:str, xlim=None, ylim=None, title:str=None, legend:bool=False):
    """
    Plots a scatter plot with a line
    :param scatter_x: x values for the scatter plot
    :param scatter_y: y values for the scatter plot
    :param scatter_properties: dictionary with properties for the scatter plot. Possible keys are: 'color', 'label', 'marker', 's', 'alpha'. Not all keys are required.
    :param line_x: x values for the line
    :param line_y: y values for the line
    :param line_properties: dictionary with properties for the line plot. Possible keys are: 'color', 'label', 'linestyle', 'linewidth'. Not all keys are required.
    :param x_label: label for the x axis
    :param y_label: label for the y axis
    :param title: title for the plot
    :param legend: boolean to show the legend
    :return: None
    """
    if xlim is not None:
        ax.set_xlim(xlim)
    if ylim is not None:
        ax.set_ylim(ylim)
    scatter_line = ax.scatter(scatter_x, scatter_y, color=scatter_properties.get('color', 'blue'), label=scatter_properties.get('label', None), marker=scatter_properties.get('marker', 'o'), s=scatter_properties.get('s', 10), alpha=scatter_properties.get('alpha', 1.0))
    plot_line = ax.plot(line_x, line_y, color=line_properties.get('color', 'red'), label=line_properties.get('label', None), linestyle=line_properties.get('linestyle', '-'), linewidth=line_properties.get('linewidth', 1.0))
    ax.set_xlabel(x_label)
    ax.set_ylabel(y_label)
    if title is not None:
        ax.set_title(title)
    if legend:
        ax.legend(loc='upper right')

    return ax, scatter_line, plot_line

def plot_scatter(ax, scatter_x, scatter_y, scatter_properties:dict, x_label:str, y_label:str, title:str=None, legend:bool=False):
    """
    Plots a scatter plot
    :param scatter_x: x values for the scatter plot
    :param scatter_y: y values for the scatter plot
    :param scatter_properties: dictionary with properties for the scatter plot. Possible keys are: 'color', 'label', 'marker', 's', 'alpha'. Not all keys are required.
    :param x_label: label for the x axis
    :param y_label: label for the y axis
    :param title: title for the plot
    :param legend: boolean to show the legend
    :return: None
    """
    scatter_line = ax.scatter(scatter_x, scatter_y, color=scatter_properties.get('color', 'blue'), label=scatter_properties.get('label', None), marker=scatter_properties.get('marker', 'o'), s=scatter_properties.get('s', 10), alpha=scatter_properties.get('alpha', 1.0))
    ax.xlabel(x_label)
    ax.ylabel(y_label)
    if title is not None:
        ax.title(title)
    if legend:
        ax.legend(loc='upper right')

    return ax, scatter_line