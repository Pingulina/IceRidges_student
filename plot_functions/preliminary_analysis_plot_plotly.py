import plotly.graph_objects as go
import scipy.stats
import numpy as np

def plot_scatter_with_line(fig, row, col, scatter_x, scatter_y, scatter_properties: dict, line_x, line_y, line_properties: dict, x_label: str, y_label: str, xlim=None, ylim=None, title: str = None, legend: bool = False):
    """
    Plots a scatter plot with a line using Plotly
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
    :return: Plotly figure
    """

    # Add scatter plot
    scatter_trace = go.Scatter(
        x=scatter_x,
        y=scatter_y,
        mode='markers',
        marker=dict(
            color=scatter_properties.get('color', 'blue'),
            symbol=scatter_properties.get('marker', 'circle'),
            size=scatter_properties.get('s', 10),
            opacity=scatter_properties.get('alpha', 1.0)
        ),
        name=scatter_properties.get('label', 'Scatter')
    )
    fig.add_trace(scatter_trace, row=row, col=col)
    scatter_index = len(fig.data) - 1

    # Add line plot
    line_trace = go.Scatter(
        x=line_x,
        y=line_y,
        mode='lines',
        line=dict(
            color=line_properties.get('color', 'red'),
            dash=line_properties.get('linestyle', 'solid'),
            width=line_properties.get('linewidth', 1.0)
        ),
        name=line_properties.get('label', 'Line')
    )
    fig.add_trace(line_trace, row=row, col=col)
    line_index = len(fig.data) - 1

    # Update axes labels
    fig.update_xaxes(title_text=x_label)
    fig.update_yaxes(title_text=y_label)

    # Set axis limits if provided
    if xlim is not None:
        fig.update_xaxes(range=xlim)
    if ylim is not None:
        fig.update_yaxes(range=ylim)

    # Set title if provided
    if title is not None:
        fig.update_layout(title_text=title)

    # Show legend if required
    if legend:
        fig.update_layout(showlegend=True)
    else:
        fig.update_layout(showlegend=False)

    return fig, scatter_index, line_index


def plot_scatter(fig, row, col, scatter_x, scatter_y, scatter_properties: dict, x_label: str, y_label: str, xlim=None, ylim=None, title: str = None, legend: bool = False):
    """
    Plots a scatter plot with a line using Plotly
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
    :return: Plotly figure
    """

    # Add scatter plot
    scatter_trace = go.Scatter(
        x=scatter_x,
        y=scatter_y,
        mode='markers',
        marker=dict(
            color=scatter_properties.get('color', 'blue'),
            symbol=scatter_properties.get('marker', 'circle'),
            size=scatter_properties.get('s', 10),
            opacity=scatter_properties.get('alpha', 1.0)
        ),
        name=scatter_properties.get('label', 'Scatter')
    )
    fig.add_trace(scatter_trace, row=row, col=col)
    scatter_index = len(fig.data) - 1

    # Update axes labels
    fig.update_xaxes(title_text=x_label)
    fig.update_yaxes(title_text=y_label)

    # Set axis limits if provided
    if xlim is not None:
        fig.update_xaxes(range=xlim)
    if ylim is not None:
        fig.update_yaxes(range=ylim)

    # Set title if provided
    if title is not None:
        fig.update_layout(title_text=title)

    # Show legend if required
    if legend:
        fig.update_layout(showlegend=True)
    else:
        fig.update_layout(showlegend=False)

    return fig, scatter_index



def plot_scatter_double(fig, row, col, scatter1_x, scatter1_y, scatter1_properties: dict, scatter2_x, scatter2_y, scatter2_properties, x_label: str, y_label: str, xlim=None, ylim=None, title: str = None, legend: bool = False):
    """
    Plots a scatter plot with a line using Plotly
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
    :return: Plotly figure
    """

    # Add scatter plot
    scatter1_trace = go.Scatter(
        x=scatter1_x,
        y=scatter1_y,
        mode='markers',
        marker=dict(
            color=scatter1_properties.get('color', 'blue'),
            symbol=scatter1_properties.get('marker', 'circle'),
            size=scatter1_properties.get('s', 10),
            opacity=scatter1_properties.get('alpha', 1.0)
        ),
        name=scatter1_properties.get('label', 'Scatter')
    )
    fig.add_trace(scatter1_trace, row=row, col=col)
    scatter1_index = len(fig.data) - 1

    scatter2_trace = go.Scatter(
        x=scatter2_x,
        y=scatter2_y,
        mode='markers',
        marker=dict(
            color=scatter2_properties.get('color', 'blue'),
            symbol=scatter2_properties.get('marker', 'circle'),
            size=scatter2_properties.get('s', 10),
            opacity=scatter2_properties.get('alpha', 1.0)
        ),
        name=scatter2_properties.get('label', 'Scatter')
    )
    fig.add_trace(scatter2_trace, row=row, col=col)
    scatter2_index = len(fig.data) - 1

    # Update axes labels
    fig.update_xaxes(title_text=x_label)
    fig.update_yaxes(title_text=y_label)

    # Set axis limits if provided
    if xlim is not None:
        fig.update_xaxes(range=xlim)
    if ylim is not None:
        fig.update_yaxes(range=ylim)

    # Set title if provided
    if title is not None:
        fig.update_layout(title_text=title)

    # Show legend if required
    if legend:
        fig.update_layout(showlegend=True)
    else:
        fig.update_layout(showlegend=False)

    return fig, scatter1_index, scatter2_index



def plot_histogram_with_line(fig, row, col, hist_data, hist_properties: dict, line_x, line_properties: dict, x_label: str, y_label: str, xlim=None, ylim=None, title: str = None, legend: bool = False):
    """
    Plots a histogram with a line using Plotly
    :param hist_data: data for the histogram
    :param hist_properties: dictionary with properties for the histogram. Possible keys are: 'color', 'label', 'bins', 'alpha', 'distribution'. Not all keys are required.
    :param line_x: x values to evaluate the hist_data probability distribution for the line
    :param line_properties: dictionary with properties for the line plot. Possible keys are: 'color', 'label', 'linestyle', 'linewidth', 'distribution'. Not all keys are required.
    :param x_label: label for the x axis
    :param y_label: label for the y axis
    :param xlim: limits for the x axis
    :param ylim: limits for the y axis
    :param title: title for the plot
    :param legend: boolean to show the legend
    :return: Plotly figure
    """

    # Determine the probability distribution
    if hist_properties.get('distribution', 'norm') == 'norm':
        prob_distri = scipy.stats.norm.fit(hist_data)
    elif hist_properties.get('distribution', 'norm') == 'nakagami':
        prob_distri = scipy.stats.nakagami.fit(hist_data)

    # Create histogram trace
    hist_trace = go.Histogram(
        x=hist_data,
        nbinsx=hist_properties.get('bins', 10),
        histnorm='probability density',
        marker=dict(
            color=hist_properties.get('color', 'blue'),
            opacity=hist_properties.get('alpha', 0.5)
        ),
        name=hist_properties.get('label', 'Histogram')
    )

    # Determine the line y-values based on the distribution
    if line_properties.get('distribution', 'norm') == 'norm':
        line_y = scipy.stats.norm.pdf(line_x, prob_distri[0], prob_distri[1])
    elif line_properties.get('distribution', 'norm') == 'nakagami':
        line_y = scipy.stats.nakagami.pdf(line_x, prob_distri[0], prob_distri[1])

    # Create line trace
    line_trace = go.Scatter(
        x=line_x,
        y=line_y,
        mode='lines',
        line=dict(
            color=line_properties.get('color', 'red'),
            dash=line_properties.get('linestyle', 'solid'),
            width=line_properties.get('linewidth', 1.0)
        ),
        name=line_properties.get('label', 'Line')
    )

    # Add traces to figure
    fig.add_trace(hist_trace, row=row, col=col)
    hist_index = len(fig.data) - 1
    fig.add_trace(line_trace, row=row, col=col)
    line_index = len(fig.data) - 1

    # Update axes labels
    fig.update_xaxes(title_text=x_label)
    fig.update_yaxes(title_text=y_label)

    # Set axis limits if provided
    if xlim is not None:
        fig.update_xaxes(range=xlim)
    if ylim is not None:
        fig.update_yaxes(range=ylim)

    # Set title if provided
    if title is not None:
        fig.update_layout(title_text=title)

    # Show legend if required
    fig.update_layout(showlegend=legend)

    return fig, prob_distri, hist_index, line_index


def plot_histogram(fig, row, col, hist_data, hist_properties: dict, x_label: str, y_label: str, title: str = None, legend: bool = False):
    """
    Plots a histogram with a line using Plotly
    :param hist_data: data for the histogram
    :param hist_properties: dictionary with properties for the histogram. Possible keys are: 'color', 'label', 'bins', 'alpha', 'distribution'. Not all keys are required.
    :param line_x: x values to evaluate the hist_data probability distribution for the line
    :param line_properties: dictionary with properties for the line plot. Possible keys are: 'color', 'label', 'linestyle', 'linewidth', 'distribution'. Not all keys are required.
    :param x_label: label for the x axis
    :param y_label: label for the y axis
    :param xlim: limits for the x axis
    :param ylim: limits for the y axis
    :param title: title for the plot
    :param legend: boolean to show the legend
    :return: Plotly figure
    """
    # Create histogram trace
    hist_trace = go.Histogram(
        x=hist_data,
        nbinsx=hist_properties.get('bins', 10),
        marker=dict(
            color=hist_properties.get('color', 'tab:blue'),
            opacity=hist_properties.get('alpha', 0.5)
        ),
        name=hist_properties.get('label', 'Histogram')
    )

    # Add trace to figure
    fig.add_trace(hist_trace, row=row, col=col)
    trace_index = len(fig.data) - 1

    # Update axes labels
    fig.update_xaxes(title_text=x_label)
    fig.update_yaxes(title_text=y_label)

    # Set title if provided
    if title is not None:
        fig.update_layout(title_text=title)

    # Show legend if required
    fig.update_layout(showlegend=legend)

    return fig, trace_index


def plot_histogram_double(fig, row, col, hist1_data, hist1_properties: dict, hist2_data, hist2_properties: dict, x_label: str, y_label: str, xlim=None, ylim=None, title: str = None, legend: bool = False):
    """
    Plots a histogram with a line using Plotly
    :param hist_data: data for the histogram
    :param hist_properties: dictionary with properties for the histogram. Possible keys are: 'color', 'label', 'bins', 'alpha', 'distribution'. Not all keys are required.
    :param line_x: x values to evaluate the hist_data probability distribution for the line
    :param line_properties: dictionary with properties for the line plot. Possible keys are: 'color', 'label', 'linestyle', 'linewidth', 'distribution'. Not all keys are required.
    :param x_label: label for the x axis
    :param y_label: label for the y axis
    :param xlim: limits for the x axis
    :param ylim: limits for the y axis
    :param title: title for the plot
    :param legend: boolean to show the legend
    :return: Plotly figure
    """

        # Create histogram trace
    hist1_trace = go.Histogram(
        x=hist1_data,
        nbinsx=hist1_properties.get('bins', 10),
        marker=dict(
            color=hist1_properties.get('color', 'tab:blue'),
            opacity=hist1_properties.get('alpha', 0.5)
        ),
        name=hist1_properties.get('label', 'Histogram')
    )

    hist2_trace = go.Histogram(
        x=hist2_data,
        nbinsx=hist2_properties.get('bins', 10),
        marker=dict(
            color=hist2_properties.get('color', 'tab:blue'),
            opacity=hist2_properties.get('alpha', 0.5)
        ),
        name=hist2_properties.get('label', 'Histogram')
    )

    # Add trace to figure
    fig.add_trace(hist1_trace)
    trace1_index = len(fig.data) - 1
    
    fig.add_trace(hist2_trace)
    trace2_index = len(fig.data) - 1

    # Update axes labels
    fig.update_xaxes(title_text=x_label)
    fig.update_yaxes(title_text=y_label)

    # Set title if provided
    if title is not None:
        fig.update_layout(title_text=title)

    # Show legend if required
    fig.update_layout(showlegend=legend)

    return fig, trace1_index, trace2_index