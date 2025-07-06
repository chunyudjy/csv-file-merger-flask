from flask import Flask, request, render_template, send_file
import pandas as pd
import io

app = Flask(__name__)
merged_buffer = None  # 缓存合并后的 CSV 内容

@app.route('/', methods=['GET', 'POST'])
def upload():
    global merged_buffer
    if request.method == 'POST':
        files = request.files.getlist('files')
        dfs = []
        filenames = []

        for f in files:
            if f and f.filename.endswith('.csv'):
                try:
                    df = pd.read_csv(f)
                    dfs.append(df)
                    filenames.append(f.filename)
                except Exception as e:
                    filenames.append(f"{f.filename} (读取失败: {e})")

        if not dfs:
            return render_template('index.html', filenames=[], preview_html=None, downloadable=False)

        # 合并所有 DataFrame
        merged_df = pd.concat(dfs, ignore_index=True)

        # 缓存合并后的 CSV 文件供下载
        merged_buffer = io.StringIO()
        merged_df.to_csv(merged_buffer, index=False)
        merged_buffer.seek(0)

        # 转换前10行为 HTML 表格
        preview_html = merged_df.head(10).to_html(classes='table table-bordered table-sm', index=False, border=0)

        return render_template(
            'index.html',
            filenames=filenames,
            preview_html=preview_html,
            downloadable=True
        )

    return render_template('index.html', preview_html=None, downloadable=False)

@app.route('/download')
def download():
    global merged_buffer
    if merged_buffer:
        return send_file(
            io.BytesIO(merged_buffer.getvalue().encode('utf-8')),
            mimetype='text/csv',
            download_name='merged_result.csv',
            as_attachment=True
        )
    return "⚠️ 没有可供下载的文件。"

if __name__ == '__main__':
    app.run(debug=True)
