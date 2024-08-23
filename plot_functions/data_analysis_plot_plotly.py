import plotly.graph_objects as go
import numpy as np

def initialize_plot_data_draft(fig, row, col, time, draft, time_ridge, draft_ridge, time_LI, draft_LI, week_starts, week_ends, week, every_nth_xTick, 
                               xlabel: str, ylabel: str, ylim, xTickLabels=None, legend=True):
    # Add the fill_between equivalent
    fig.add_trace(go.Scatter(
        x=[week_starts[week], week_ends[week], week_ends[week], week_starts[week]],
        y=[0, 0, max(draft), max(draft)],
        fill='toself',
        fillcolor='lightblue',
        line=dict(color='lightblue'),
        name='Current week ice data',
        mode='none'
    ), row=row, col=col)

    # Add the ULS draft signal plot
    fig.add_trace(go.Scatter(
        x=time,
        y=draft,
        mode='lines',
        line=dict(color='blue'),
        name='Raw ULS draft signal'
    ), row=row, col=col)

    # Add the Ridge Peaks scatter plot
    keel_draft_flat = [x for xs in draft_ridge for x in xs]
    keel_dateNum_flat = [x for xs in time_ridge for x in xs]
    print(f"keel_dateNum_flat: {keel_dateNum_flat}")
    print(f"keel_draft_flat: {keel_draft_flat}")
    fig.add_trace(go.Scatter(
        x=keel_dateNum_flat,
        y=keel_draft_flat,
        mode='markers',
        marker=dict(color='red', size=3),
        name='Individual ridge peaks'
    ), row=row, col=col)

    # Add the Level ice draft estimate step plot
    keel_dateNum_weekStart = [date[0] for date in time_LI]
    fig.add_trace(go.Scatter(
        x=keel_dateNum_weekStart,
        y=draft_LI,
        mode='lines',
        line=dict(color='black'),
        name='Level ice draft estimate',
        line_shape='hv'
    ), row=row, col=col)

    # Update layout
    fig.update_yaxes(title_text=ylabel, range=[ylim[0], ylim[1]], row=row, col=col)
    fig.update_xaxes(title_text=xlabel, row=row, col=col)

    # Update x-axis ticks and labels
    dateNum_every_day = time[np.where(np.diff(time.astype(int)))[0] + 1]
    fig.update_xaxes(
        tickvals=dateNum_every_day[::every_nth_xTick],
        ticktext=xTickLabels[::every_nth_xTick] if xTickLabels is not None else None,
        range=[time[0], time[-1]],
        automargin=True,
        row=row, col=col
    )

    return fig