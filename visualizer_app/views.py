import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import io
import base64
from django.shortcuts import render
from django.core.files.storage import FileSystemStorage
from django.http import FileResponse
import os

def home(request):
    data_preview = None
    columns = None
    plot_url = None
    error_message = None

    if request.method == 'POST' and request.FILES.get('file'):
        # Handle file upload
        uploaded_file = request.FILES['file']
        fs = FileSystemStorage()
        filename = fs.save(uploaded_file.name, uploaded_file)
        file_path = fs.url(filename)

        # Load CSV file
        try:
            data = pd.read_csv(file_path[1:])  # Skip leading slash
            data_preview = data.head(10).to_html(classes='data table table-bordered', index=False)
            columns = data.columns.tolist()  # Extract all columns for dropdowns
            request.session['data_csv'] = data.to_csv(index=False)  # Save data to session
        except Exception as e:
            error_message = f"Error loading file: {str(e)}"

    if request.method == 'POST' and 'column_x' in request.POST and 'column_y' in request.POST and 'plot_type' in request.POST:
        # Handle plot generation
        column_x = request.POST['column_x']
        column_y = request.POST['column_y']
        plot_type = request.POST['plot_type']

        try:
            data = pd.read_csv(io.StringIO(request.session.get('data_csv')))
            if column_x in data.columns and column_y in data.columns:
                # Dynamically adjust plot size based on the data length
                num_x_labels = len(data[column_x].unique())
                plot_width = max(num_x_labels * 0.6, 10)  # Adjust width based on unique x values
                plot_height = 6  # Fixed height for consistency

                plt.figure(figsize=(plot_width, plot_height))

                # Generate the selected plot type
                if plot_type == 'line':
                    plt.plot(data[column_x], data[column_y], marker='o')
                elif plot_type == 'bar':
                    plt.bar(data[column_x], data[column_y])
                elif plot_type == 'scatter':
                    plt.scatter(data[column_x], data[column_y])
                elif plot_type == 'histogram':
                    plt.hist(data[column_y], bins=20)
                elif plot_type == 'box':
                    sns.boxplot(x=data[column_x], y=data[column_y])
                elif plot_type == 'area':
                    plt.fill_between(data[column_x], data[column_y], alpha=0.5)
                elif plot_type == 'bubble':
                    plt.scatter(data[column_x], data[column_y], s=data[column_y] * 10, alpha=0.5)
                elif plot_type == 'heatmap':
                    sns.heatmap(data.corr(), annot=True, cmap='coolwarm')
                elif plot_type == 'stacked_bar':
                    data.groupby(column_x)[column_y].sum().plot(kind='bar', stacked=True)
                elif plot_type == 'violin':
                    sns.violinplot(x=data[column_x], y=data[column_y])
                elif plot_type == 'waterfall':
                    diffs = data[column_y].diff().fillna(data[column_y])
                    plt.bar(data[column_x], diffs, bottom=data[column_y].cumsum() - diffs)
                elif plot_type == 'pairplot':
                    sns.pairplot(data, diag_kind='kde')
                elif plot_type == 'density':
                    sns.kdeplot(data[column_y], fill=True)
                elif plot_type == 'swarm':
                    sns.swarmplot(x=data[column_x], y=data[column_y])
                elif plot_type == 'regression':
                    sns.regplot(x=data[column_x], y=data[column_y])

                # Customize and save the plot
                plt.title(f'{plot_type.capitalize()} Plot: {column_x} vs {column_y}')
                plt.xlabel(column_x)
                plt.ylabel(column_y)
                plt.xticks(rotation=45, ha='right')  # Rotate x-axis labels for better readability
                plt.grid(True)

                buf = io.BytesIO()
                plt.savefig(buf, format='png')
                buf.seek(0)
                plot_url = base64.b64encode(buf.read()).decode('utf-8')
                buf.close()

                # Save plot to disk for download
                plot_path = f"media/plot_{column_x}_{column_y}.png"
                plt.savefig(plot_path)
                request.session['plot_path'] = plot_path
                plt.close()

            else:
                error_message = "Invalid column selection."
        except Exception as e:
            error_message = f"Error generating plot: {str(e)}"

    return render(request, 'visualizer_app/home.html', {
        'data_preview': data_preview,
        'columns': columns,
        'plot_url': plot_url,
        'error_message': error_message,
    })

def download_plot(request):
    plot_path = request.session.get('plot_path')

    if plot_path and os.path.exists(plot_path):
        # Serve the plot file as a response
        response = FileResponse(open(plot_path, 'rb'), content_type='image/png')
        response['Content-Disposition'] = f'attachment; filename={os.path.basename(plot_path)}'
        return response
    else:
        # Return an error response if the file does not exist
        return HttpResponse("Plot not found.", status=404)
