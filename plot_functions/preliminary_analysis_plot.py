# plot functions for different analysis plots

import numpy as np
import matplotlib.pyplot as plt
import scipy.stats




def plot_scatter_with_line(ax, scatter_x, scatter_y, scatter_properties:dict, line_x, line_y, line_properties:dict, x_label:str, y_label:str, xlim=None, ylim=None, title:str=None, legend:bool=False):
    """
    Plots a scatter plot with a line
    :param ax: axis for the plot
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

def plot_scatter(ax, scatter_x, scatter_y, scatter_properties:dict, x_label:str, y_label:str, xlim=None, ylim=None, title:str=None, legend:bool=False):
    """
    Plots a scatter plot
    :param ax: axis for the plot
    :param scatter_x: x values for the scatter plot
    :param scatter_y: y values for the scatter plot
    :param scatter_properties: dictionary with properties for the scatter plot. Possible keys are: 'color', 'label', 'marker', 's', 'alpha'. Not all keys are required.
    :param x_label: label for the x axis
    :param y_label: label for the y axis
    :param x_lim: tuple with the limits for the x axis
    :param y_lim: tuple with the limits for the y axis
    :param title: title for the plot
    :param legend: boolean to show the legend
    :return: ax, scatter_line
    """
    if xlim is not None:
        ax.set_xlim(xlim)
    if ylim is not None:
        ax.set_ylim(ylim)
    scatter_line = ax.scatter(scatter_x, scatter_y, color=scatter_properties.get('color', 'blue'), label=scatter_properties.get('label', None), marker=scatter_properties.get('marker', 'o'), s=scatter_properties.get('s', 10), alpha=scatter_properties.get('alpha', 1.0))
    ax.set_xlabel(x_label)
    ax.set_ylabel(y_label)
    if title is not None:
        ax.set_title(title)
    if legend:
        ax.legend(loc='upper right')

    return ax, scatter_line

def plot_scatter_double(ax, scatter1_x, scatter1_y, scatter1_properties:dict, scatter2_x, scatter2_y, scatter2_properties:dict, x_label:str, y_label:str, xlim=None, ylim=None, title:str=None, legend:bool=False):
    """
    Plots a scatter plot
    :param ax: axis for the plot
    :param scatter_x: x values for the scatter plot
    :param scatter_y: y values for the scatter plot
    :param scatter_properties: dictionary with properties for the scatter plot. Possible keys are: 'color', 'label', 'marker', 's', 'alpha'. Not all keys are required.
    :param x_label: label for the x axis
    :param y_label: label for the y axis
    :param x_lim: tuple with the limits for the x axis
    :param y_lim: tuple with the limits for the y axis
    :param title: title for the plot
    :param legend: boolean to show the legend
    :return: ax, scatter_line
    """
    if xlim is not None:
        ax.set_xlim(xlim)
    if ylim is not None:
        ax.set_ylim(ylim)
    scatter1_line = ax.scatter(scatter1_x, scatter1_y, color=scatter1_properties.get('color', 'blue'), label=scatter1_properties.get('label', None), marker=scatter1_properties.get('marker', 'o'), s=scatter1_properties.get('s', 10), alpha=scatter1_properties.get('alpha', 1.0))
    scatter2_line = ax.scatter(scatter2_x, scatter2_y, color=scatter2_properties.get('color', 'red'), label=scatter2_properties.get('label', None), marker=scatter2_properties.get('marker', 'o'), s=scatter2_properties.get('s', 10), alpha=scatter2_properties.get('alpha', 1.0))

    ax.set_xlabel(x_label)
    ax.set_ylabel(y_label)
    if title is not None:
        ax.set_title(title)
    if legend:
        ax.legend(loc='upper right')

    return ax, scatter1_line, scatter2_line

def plot_histogram_with_line(ax, hist_data, hist_properties:dict, line_x, line_properties:dict, x_label:str, y_label:str, xlim=None, ylim=None, title:str=None, legend:bool=False):
    """
    Plots a histogram
    :param ax: axis for the plot
    :param hist_data: data for the histogram
    :param hist_properties: dictionary with properties for the histogram. Possible keys are: 'color', 'label', 'bins', 'alpha'. Not all keys are required.
    :param line_x: x values to evaluate the hist_data probability distribtion for the line
    :param line_properties: dictionary with properties for the line plot. Possible keys are: 'color', 'label', 'linestyle', 'linewidth'. Not all keys are required.
    :param x_label: label for the x axis
    :param y_label: label for the y axis
    :param title: title for the plot
    :param legend: boolean to show the legend
    :return: ax, scatter_line
    """
    if xlim is not None:
        ax.set_xlim(xlim)
    if ylim is not None:
        ax.set_ylim(ylim)

    if hist_properties.get('distribution', 'norm') == 'norm':
        prob_distri = scipy.stats.norm.fit(hist_data)
    elif hist_properties.get('distribution', 'norm') == 'nakagami':
        prob_distri = scipy.stats.nakagami.fit(hist_data)

    # plot the histogram
    hist_numpy = np.histogram(hist_data, bins=hist_properties.get('bins', 10), density=True)
    hist_line = ax.bar(hist_numpy[1][:-1], hist_numpy[0], align='edge', color=hist_properties.get('color', 'tab-blue'), alpha=hist_properties.get('alpha', 0.5), 
                       zorder=0, width=(max(hist_data)-min(hist_data))/hist_properties.get('bins', 10))
    
    # plot the distribution line
    if line_properties.get('distribution', 'norm') == 'norm':
        prob_distri = scipy.stats.norm.fit(hist_data)
        line_y = scipy.stats.norm.pdf(line_x, prob_distri[0], prob_distri[1])
    elif line_properties.get('distribution', 'norm') == 'nakagami':
        prob_distri = scipy.stats.nakagami.fit(hist_data)
        line_y = scipy.stats.nakagami.pdf(line_x, prob_distri[0], prob_distri[1])
    plot_line = ax.plot(line_x, line_y, color=line_properties.get('color', 'red'), label=line_properties.get('label', None), 
                        linestyle=line_properties.get('linestyle', '-'), linewidth=line_properties.get('linewidth', 1.0))

    
    ax.set_xlabel(x_label)
    ax.set_ylabel(y_label)
    if title is not None:
        ax.set_title(title)
    if legend:
        ax.legend(loc='upper right')

    return ax, hist_line, plot_line, prob_distri

def plot_histogram(ax, hist_data, hist_properties:dict, x_label:str, y_label:str, title:str=None, legend:bool=False):
    """
    Plots a histogram
    :param ax: axis for the plot
    :param hist_x: x values for the histogram
    :param hist_y: y values for the histogram
    :param hist_properties: dictionary with properties for the histogram. Possible keys are: 'color', 'label', 'bins', 'alpha'. Not all keys are required.
    :param x_label: label for the x axis
    :param y_label: label for the y axis
    :param title: title for the plot
    :param legend: boolean to show the legend
    :return: ax, hist_line
    """
    hist_numpy = np.histogram(hist_data, bins=hist_properties.get('bins', 10))
    hist_line = ax.bar(hist_numpy[1][:-1], hist_numpy[0], align='edge', color=hist_properties.get('color', 'tab-blue'), alpha=hist_properties.get('alpha', 0.5), 
                       zorder=0, width=(max(hist_data)-min(hist_data))/hist_properties.get('bins', 10))
    
    ax.set_xlabel(x_label)
    ax.set_ylabel(y_label)
    if title is not None:
        ax.set_title(title)
    if legend:
        ax.legend(loc='upper right')

    return ax, hist_line



def plot_histogram_double(ax, hist1_data, hist1_properties:dict, hist2_data, hist2_properties:dict, x_label:str, y_label:str, title:str=None, legend:bool=False):
    """
    Plots a histogram
    :param ax: axis for the plot
    :param hist1_data: data for the first histogram
    :param hist1_properties: dictionary with properties for the first histogram. Possible keys are: 'color', 'label', 'bins', 'alpha'. Not all keys are required.
    :param hist2_data: data for the second histogram
    :param hist2_properties: dictionary with properties for the second histogram. Possible keys are: 'color', 'label', 'bins', 'alpha'. Not all keys are required.
    :param x_label: label for the x axis
    :param y_label: label for the y axis
    :param title: title for the plot
    :param legend: boolean to show the legend
    :return: ax, hist_line
    """

    hist1_numpy = np.histogram(hist1_data, bins=hist1_properties.get('bins', 10), density=hist1_properties.get('density', False))
    hist1_line = ax.bar(hist1_numpy[1][:-1], hist1_numpy[0], align='edge', color=hist1_properties.get('color', 'tab-blue'), alpha=hist1_properties.get('alpha', 0.5), 
                       zorder=0, width=(max(hist1_data)-min(hist1_data))/hist1_properties.get('bins', 10))
    
    hist2_numpy = np.histogram(hist2_data, bins=hist2_properties.get('bins', 10), density=hist2_properties.get('density', False))
    hist2_line = ax.bar(hist2_numpy[1][:-1], hist2_numpy[0], align='edge', color=hist2_properties.get('color', 'tab-red'), alpha=hist2_properties.get('alpha', 0.5), 
                       zorder=0, width=(max(hist2_data)-min(hist2_data))/hist2_properties.get('bins', 10))
    
    ax.set_xlabel(x_label)
    ax.set_ylabel(y_label)
    if title is not None:
        ax.set_title(title)
    if legend:
        ax.legend(loc='upper right')

    return ax, hist1_line, hist2_line