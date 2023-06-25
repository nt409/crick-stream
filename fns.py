from urllib.request import urlopen, Request
from bs4 import BeautifulSoup


def get_data(url):

    soup = get_soup(url)

    teams = soup.find_all("p", class_="team-name")[:2]

    scores = soup.find_all("p", class_="team-info-2")[:2]

    out = []

    for team_ind in range(2):
        team_text = get_scores(teams[team_ind], scores[team_ind])
        out.append(team_text)

    return out


def get_soup(url):

    req = Request(
        url,
        headers={
            'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:52.0) Gecko/20100101 Firefox/52.0'
        }
    )

    html = urlopen(req)

    soup = BeautifulSoup(html, "html.parser")

    return soup


def get_scores(team_raw, score_raw):

    # TEAM

    team_name = (
        str(team_raw)
        .split('>')[1]
        .split('<')[0]
        .strip()
        [:3]
        .upper()
    )

    # WICKETS

    wkts = (
        str(score_raw)
        .split(' / ')[1:]
    )

    wkts_list = []

    for ww in wkts:
        w_str = (
            ww
            .split('</span>')[0]
            .strip()
            .upper()
            .replace('OVERS', '')
            .replace('  ', ' ')
            .replace('( ', '(')
            .replace(' )', ')')
            .replace('ALL OUT', '10')
        )

        w_str = '/ ' + w_str

        wkts_list.append(w_str)

    # RUNS

    runs = (
        str(score_raw)
        .split('</span>')[1:-1]
    )

    runs_list = []

    for rr in runs:
        run = (
            rr
            .split('<span class="smalltxt">')[0]
            .replace('<br/>', '')
            .strip()
        )

        runs_list.append(run)

    # INNINGS TEXT

    innings_text = ""
    for inns in range(len(runs_list)):
        if inns == 1:
            add_sign_text = ' & '

            # shouldn't be needed but there as a failsafe
            if len(wkts_list) < 2:
                wkts_list.append('')

        else:
            add_sign_text = ''

        innings_text += f"{add_sign_text}{runs_list[inns]} {wkts_list[inns]}"

    out = f"{team_name}: {innings_text}"

    return out


def write_files(data):
    home = data[0]
    away = data[1]

    write_file(home, 'home')
    write_file(away, 'away')


def write_file(text, name):
    file_name = f"scores/{name}.txt"
    file_ = open(file_name, 'w')
    file_.writelines(text)
    print(f"writing: {text}")


if __name__ == "__main__":
    URL = "https://cambridgeuniversity.play-cricket.com/website/results/5690698"

    text = get_data(URL)

    print(text)
