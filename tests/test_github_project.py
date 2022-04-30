import time
from playwright.sync_api import APIRequestContext, Page, expect


def test_create_project_card(
        gh_context: APIRequestContext,
        project_column_ids: list[str]) -> None:
    now = time.time()
    note = f'A new task at {now}'

    c_response = gh_context.post(
        f'/projects/columns/{project_column_ids[0]}/cards',
        data={'note': note})
    expect(c_response).to_be_ok()
    assert c_response.json()['note'] == note

    card_id = c_response.json()['id']
    r_response = gh_context.get(f'/projects/columns/cards/{card_id}')
    expect(r_response).to_be_ok()
    assert r_response.json() == c_response.json()


def test_move_project_card(
    gh_context: APIRequestContext,
    gh_project: dict,
    project_column_ids: list[str],
    page: Page,
    gh_username: str,
    gh_password: str) -> None:

    source_col = project_column_ids[0]
    dest_col = project_column_ids[1]
    now = time.time()
    note = f'Move this card at {now}'
    c_response = gh_context.post(
        f'/projects/columns/{source_col}/cards',
        data={'note': note})
    expect(c_response).to_be_ok()

    page.goto(f'https://github.com/login')
    page.locator('id=login_field').fill(gh_username)
    page.locator('id=password').fill(gh_password)
    page.locator('input[name="commit"]').click()

    page.goto(f'https://github.com/users/{gh_username}/projects/{gh_project["number"]}')

    card_xpath = f'//div[@id="column-cards-{source_col}"]//p[contains(text(), "{note}")]'
    expect(page.locator(card_xpath)).to_be_visible()

    page.drag_and_drop(f'text="{note}"', f'id=column-cards-{dest_col}')

    card_xpath = f'//div[@id="column-cards-{dest_col}"]//p[contains(text(), "{note}")]'
    expect(page.locator(card_xpath)).to_be_visible()

    card_id = c_response.json()['id']
    r_response = gh_context.get(f'/projects/columns/cards/{card_id}')
    expect(r_response).to_be_ok()
    assert r_response.json()['column_url'].endswith(str(dest_col))
