from bs4 import BeautifulSoup


def assert_has_h1(soup):
    assert soup.find('h1') is not None, 'Missing <h1> on page'


def assert_inputs_have_labels(soup):
    # For each input/textarea/select, ensure there is an associated label
    inputs = soup.find_all(['input', 'textarea', 'select'])
    for inp in inputs:
        # ignore inputs of type hidden
        if inp.name == 'input' and inp.get('type') == 'hidden':
            continue

        has_label = False
        # 1) input wrapped by a <label>
        if inp.find_parent('label'):
            has_label = True

        # 2) label with for matching id
        inp_id = inp.get('id')
        if inp_id and soup.find('label', attrs={'for': inp_id}):
            has_label = True

        assert has_label, f'Form control missing label: {str(inp)[:80]}'


def assert_buttons_have_name(soup):
    for btn in soup.find_all('button'):
        if not btn.get_text(strip=True) and not btn.get('aria-label'):
            assert False, 'Button without accessible name'


def assert_links_have_text(soup):
    for a in soup.find_all('a'):
        # allow anchors with icons if they have title or aria-label
        text = a.get_text(strip=True)
        if not text and not a.get('title') and not a.get('aria-label'):
            assert False, 'Anchor with no text or accessible name'


def check_page(client, path):
    resp = client.get(path)
    assert resp.status_code == 200
    soup = BeautifulSoup(resp.data, 'html.parser')
    assert_has_h1(soup)
    assert_inputs_have_labels(soup)
    assert_buttons_have_name(soup)
    assert_links_have_text(soup)


def test_index_accessibility(client):
    check_page(client, '/')


def test_create_accessibility(client):
    check_page(client, '/create')


def test_take_and_result_accessibility(client, sample_quiz):
    # take page
    check_page(client, f'/take/{sample_quiz.id}')

    # post answers to get result page and check it
    post_data = {'question-0': '1', 'question-1': '1'}
    resp = client.post(f'/take/{sample_quiz.id}', data=post_data)
    assert resp.status_code == 200
    soup = BeautifulSoup(resp.data, 'html.parser')
    # result page should have h1 and accessible lists
    assert_has_h1(soup)
    # Ensure details list exists
    assert soup.find('ul') is not None
    assert_buttons_have_name(soup)