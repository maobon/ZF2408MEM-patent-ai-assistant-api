from flask import Flask, Blueprint, request, send_file, render_template, jsonify
import asyncio, shortuuid
from pyppeteer import launch
from multiprocessing import Process, Pipe

from swagger_server.models.cors.cors import make_cors_response
import os
os.environ['PYPPETEER_DOWNLOAD_HOST'] = 'https://npm.taobao.org/mirrors'

createPdf = Blueprint('createPdf', __name__)


async def html_to_pdf(html_content, output_path):
    browser = await launch(executablePath='/usr/bin/chromium', headless=True, args=['--no-sandbox', '--disable-dev-shm-usage'])
    # browser = await launch(headless=True)
    page = await browser.newPage()
    await page.setContent(html_content)
    await page.waitForSelector("canvas", {'timeout': 180000})  # 等待 canvas 元素加载完成
    await page.pdf({'path': output_path, 'width': '1200px'})
    await browser.close()


def generate_pdf_process(html_content, pdf_path, conn):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(html_to_pdf(html_content, pdf_path))
    conn.send('done')
    conn.close()


@createPdf.route('/generate-pdf', methods=['OPTIONS', 'POST'])
def generate_pdf():
    if request.method == 'OPTIONS':
        return make_cors_response('', 200)
    reqdata = request.get_json()
    if not reqdata or 'reportId' not in reqdata:
        return make_cors_response(jsonify({"error": "No reportId provided"}), 400)

    reportId = reqdata['reportId']
    htmlData = {
        'id': reportId
    }
    html_content = render_template('frame.html', data=htmlData)
    pdf_path = reportId+".pdf"

    parent_conn, child_conn = Pipe()
    p = Process(target=generate_pdf_process, args=(html_content, pdf_path, child_conn))
    p.start()
    p.join()

    if parent_conn.recv() == 'done':
        return make_cors_response(send_file(pdf_path, as_attachment=True))
    else:
        return make_cors_response(jsonify({"error": "Failed to generate PDF"}), 500)



@createPdf.route('/generate-pdf-test', methods=['OPTIONS', 'POST'])
def generate_pdf_test():
    if request.method == 'OPTIONS':
        return make_cors_response('', 200)
    reqdata = request.get_json()
    if not reqdata or 'reportId' not in reqdata:
        return make_cors_response(jsonify({"error": "No reportId provided"}), 400)

    reportId = reqdata['reportId']
    htmlData = {
        'id': reportId
    }
    html_content = render_template('test.html', data=htmlData)
    pdf_path = reportId+".pdf"

    parent_conn, child_conn = Pipe()
    p = Process(target=generate_pdf_process, args=(html_content, pdf_path, child_conn))
    p.start()
    p.join()

    if parent_conn.recv() == 'done':
        return make_cors_response(send_file(pdf_path, as_attachment=True))
    else:
        return make_cors_response(jsonify({"error": "Failed to generate PDF"}), 500)


def generate_short_uuid():
    return shortuuid.ShortUUID().random(length=22)
