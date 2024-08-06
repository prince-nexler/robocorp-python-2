from time import sleep
from robocorp.tasks import task
from robocorp import browser
from RPA.HTTP import HTTP
from RPA.Tables import Tables
from RPA.PDF import PDF
import os
import base64
from RPA.Archive import Archive


RECEIPTS_DIR = "output/receipts"


@task
def order_robots_from_RobotSpareBin():
    """
    Orders robots from RobotSpareBin Industries Inc.
    Saves the order HTML receipt as a PDF file.
    Saves the screenshot of the ordered robot.
    Embeds the screenshot of the robot to the PDF receipt.
    Creates ZIP archive of the receipts and the images.
    """
    browser.configure(
        slowmo=100,
        headless=False
    )
    os.makedirs(RECEIPTS_DIR, exist_ok=True)
    orders = get_orders()
    open_robot_order_website()
    fill_the_form(orders)
    archive_receipts()


def archive_receipts():
    lib = Archive()
    lib.archive_folder_with_zip(RECEIPTS_DIR, 'archive.zip', recursive=True)


def order_robot():
    page = browser.page()
    while True:
        page.click("//button[@id='order']")  # click order
        page.wait_for_selector(
            "div[class='alert alert-success'], div[class='alert alert-danger']", timeout=100)
        if page.is_visible("div[class='alert alert-success']") == True:
            break


def screenshot_robot():
    page = browser.page()
    image = page.query_selector(
        "div[id='robot-preview-image']").screenshot()
    return base64.b64encode(image).decode()


def print_receipt(order_num):
    page = browser.page()
    reciept_text = page.locator("#receipt").inner_html()
    pdf = PDF()

    image = screenshot_robot()
    reciept_text += "<div><img src='data:image/png;base64,{}'></div>".format(
        image)
    pdf.html_to_pdf(reciept_text, os.path.join(
        RECEIPTS_DIR, f"{str(order_num)}.pdf"))
    return


def fill_the_form(orders):
    page = browser.page()
    for order in orders:
        close_annoying_modal()
        print("Here")
        # {'Order number': '1', 'Head': '1', 'Body': '2', 'Legs': '3', 'Address': 'Address 123'}
        page.select_option("select[id='head']", order["Head"])
        page.set_checked(f"input[id='id-body-{order['Body']}']", order["Body"])
        page.fill("input[class='form-control']:first-of-type", order["Legs"])
        page.fill("input[id='address']", order["Address"])
        page.click("button[id='preview']")
        order_robot()
        print_receipt(order["Order number"])

        page.click("button[id='order-another']")
        # ("//button[normalize-space()='Show model info']")  # click show modal info
        # select head ("//button[@id='order']")  # click order
        print(order)
        pass


def get_orders():

    http = HTTP()
    http.download(
        url="https://robotsparebinindustries.com/orders.csv", overwrite=True)
    tablesLibrary = Tables()
    orders = tablesLibrary.read_table_from_csv(
        "orders.csv", columns=["Order number", "Head", "Body", "Legs", "Address"])
    return orders


def open_robot_order_website():
    browser.goto("https://robotsparebinindustries.com/#/robot-order")


def close_annoying_modal():
    page = browser.page()
    page.wait_for_selector("button[class='btn btn-dark']", timeout=100)
    page.click("button[class='btn btn-dark']")
