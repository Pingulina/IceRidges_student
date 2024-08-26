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
    # print(f"keel_dateNum_flat: {keel_dateNum_flat}")
    # print(f"keel_draft_flat: {keel_draft_flat}")
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
    fig.update_xaxes(title_text=xlabel, row=row, col=col)
    fig.update_yaxes(title_text=ylabel, range=[ylim[0], ylim[1]], row=row, col=col)

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


def initialize_plot_weekly_data_draft(fig, row, col, time, draft, time_ridge, draft_ridge, time_LI, draft_LI, week, 
                                      xlabel: str, ylabel: str, ylim, xTickLabels=None, dateTickDistance=1):

    # Convert time to np.array
    time = np.array(time)
    print(f"time: {time}")
    print(f"time[week]: {time[week]}")
    dateNum_every_day = time[week][np.where(np.diff(time[week].astype(int)))[0] + 1]

    # Add the Raw ULS draft signal line plot
    fig.add_trace(go.Scatter(
        x=time[week],
        y=draft[week],
        mode='lines',
        line=dict(color='blue'),
        name='Raw ULS draft signal'
    ), row=row, col=col)

    # Add the Individual ridge peaks scatter plot
    fig.add_trace(go.Scatter(
        x=time_ridge[week],
        y=draft_ridge[week],
        mode='markers',
        marker=dict(color='red', size=2),
        name='Individual ridge peaks'
    ), row=row, col=col)

    # Add the Level ice draft estimate step plot
    keel_dateNum_weekStart = [date[0] for date in time_LI]
    fig.add_trace(go.Scatter(
        x=[keel_dateNum_weekStart[week], keel_dateNum_weekStart[week+1]],
        y=[draft_LI[week], draft_LI[week]],
        mode='lines',
        line=dict(color='green'),
        name='Level ice draft estimate',
        line_shape='hv'
    ), row=row, col=col)

    # Update layout
    fig.update_xaxes(title_text=xlabel, row=row, col=col)
    fig.update_yaxes(title_text=ylabel, range=[ylim[0], ylim[1]], row=row, col=col)
    

    # Update x-axis ticks and labels
    fig.update_xaxes(
        tickvals=dateNum_every_day[:7:dateTickDistance],
        ticktext=xTickLabels[week*7:(week+1)*7:dateTickDistance] if xTickLabels is not None else None,
        row=row, col=col,
        automargin=True,
        range=[time[week][0], time[week][-1]]
    )

    return fig


def initialize_plot_spectrum(fig, row, col, HHi_plot, X_spectogram, Y_spectogram, draft, time_mean, LI_deepestMode, LI_deepestMode_expect, week_starts, week_ends, week, xlabel, ylabel):


    # Add the color mesh (pcolormesh equivalent)
    fig.add_trace(go.Heatmap(
        z=HHi_plot,
        x=X_spectogram,
        y=Y_spectogram,
        colorscale='Viridis',
        showscale=True,
    ), row=row, col=col)

    # # Add the current week ice data patch
    # fig.add_trace(go.Scatter(
    #     x=[week_starts[week], week_ends[week], week_ends[week], week_starts[week], week_starts[week]],
    #     y=[0, 0, max(draft), max(draft), 0],
    #     fill='toself',
    #     fillcolor='lightblue',
    #     line=dict(color='lightblue'),
    #     name='Current week ice data',
    #     mode='lines',
    # ), row=row, col=col)

    # # Add the scatter plot for LI_deepestMode
    # fig.add_trace(go.Scatter(
    #     x=time_mean,
    #     y=LI_deepestMode,
    #     mode='markers',
    #     marker=dict(color='red', size=10, symbol='circle'),
    #     name='LI deepest mode',
    # ), row=row, col=col)

    # # Add the scatter plot for LI_deepestMode_expect
    # fig.add_trace(go.Scatter(
    #     x=time_mean,
    #     y=LI_deepestMode_expect,
    #     mode='markers',
    #     marker=dict(color='blue', size=10, symbol='triangle-up'),
    #     name='LI deepest mode expected',
    # ), row=row, col=col)

    # # Add the rectangle patch for the current week
    # lrs1x = (time_mean[-1] - time_mean[0]) / 20
    # lrs1y = 4 / 20
    # fig.add_shape(type='rect',
    #               x0=time_mean[week] - lrs1x / 2, y0=LI_deepestMode[week] - lrs1y / 2,
    #               x1=time_mean[week] + lrs1x / 2, y1=LI_deepestMode[week] + lrs1y / 2,
    #               line=dict(color='red'),
    #               fillcolor='rgba(0,0,0,0)',
    #               layer='above',
    #               )
    

     # Update layout
    fig.update_xaxes(title_text=xlabel, range=[time_mean[0]+3.5, time_mean[-1]-10.5], row=row, col=col)
    fig.update_yaxes(title_text=ylabel, range=[0, 4], row=row, col=col)

    # fig.update_xaxes(
    #     row=row, col=col,
    #     automargin=True,
    #     range=[time_mean[0]+3.5, time_mean[-1]-10.5]
    # )

    return fig