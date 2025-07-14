from build_balance_sheet import get_balance_sheet
from pprint import pprint as pretty_print
from multiprocessing import freeze_support   # <-- Windows only (safe elsewhere)

q_filings = {
    1737523: 'https://www.sec.gov/Archives/edgar/data/1737523/000147793225003821/0001477932-25-003821-index.html',
    1820302: 'https://www.sec.gov/Archives/edgar/data/1820302/000162828025024743/0001628280-25-024743-index.html',
    1901799: 'https://www.sec.gov/Archives/edgar/data/1901799/000095017025072051/0000950170-25-072051-index.html',
    1788230: 'https://www.sec.gov/Archives/edgar/data/1788230/000178823025000062/0001788230-25-000062-index.html',
    1865602: 'https://www.sec.gov/Archives/edgar/data/1865602/000121390025044273/0001213900-25-044273-index.html',
    1805526: 'https://www.sec.gov/Archives/edgar/data/1805526/000121390025042977/0001213900-25-042977-index.html',
    1849635: 'https://www.sec.gov/Archives/edgar/data/1849635/000114036125018209/0001140361-25-018209-index.html',
    1360442: 'https://www.sec.gov/Archives/edgar/data/1360442/000109690625000870/0001096906-25-000870-index.html',
    1922858: 'https://www.sec.gov/Archives/edgar/data/1922858/000121390025046180/0001213900-25-046180-index.html',
    1889123: 'https://www.sec.gov/Archives/edgar/data/1889123/000095017025072818/0000950170-25-072818-index.html',
    1687542: 'https://www.sec.gov/Archives/edgar/data/1687542/000164117225011165/0001641172-25-011165-index.html',
    1641398: 'https://www.sec.gov/Archives/edgar/data/1641398/000121390025044218/0001213900-25-044218-index.html',
    1830072: 'https://www.sec.gov/Archives/edgar/data/1830072/000168316825003710/0001683168-25-003710-index.html',
    2022308: 'https://www.sec.gov/Archives/edgar/data/2022308/000192998025000446/0001929980-25-000446-index.html',
    1074828: 'https://www.sec.gov/Archives/edgar/data/1074828/000165495425005607/0001654954-25-005607-index.html',
    1662684: 'https://www.sec.gov/Archives/edgar/data/1662684/000141057825001326/0001410578-25-001326-index.html',
    1050446: 'https://www.sec.gov/Archives/edgar/data/1050446/000095017025063536/0000950170-25-063536-index.html',
    1946573: 'https://www.sec.gov/Archives/edgar/data/1946573/000164117225009328/0001641172-25-009328-index.html',
    1836875: 'https://www.sec.gov/Archives/edgar/data/1836875/000183687525000102/0001836875-25-000102-index.html',
    1784970: 'https://www.sec.gov/Archives/edgar/data/1784970/000121390025041307/0001213900-25-041307-index.html',
    1849380: 'https://www.sec.gov/Archives/edgar/data/1849380/000164117225010321/0001641172-25-010321-index.html',
    1981535: 'https://www.sec.gov/Archives/edgar/data/1981535/000164117225010881/0001641172-25-010881-index.html',
    2015947: 'https://www.sec.gov/Archives/edgar/data/2015947/000141057825001232/0001410578-25-001232-index.html',
    1554859: 'https://www.sec.gov/Archives/edgar/data/1554859/000155485925000020/0001554859-25-000020-index.html',
    1571934: 'https://www.sec.gov/Archives/edgar/data/1571934/000141057825001327/0001410578-25-001327-index.html',
    1853825: 'https://www.sec.gov/Archives/edgar/data/1853825/000164117225011020/0001641172-25-011020-index.html',
    1775194: 'https://www.sec.gov/Archives/edgar/data/1775194/000147793225003866/0001477932-25-003866-index.html',
    1671941: 'https://www.sec.gov/Archives/edgar/data/1671941/000155837025007836/0001558370-25-007836-index.html',
    1816937: 'https://www.sec.gov/Archives/edgar/data/1816937/000164117225011696/0001641172-25-011696-index.html'
}

def main() -> None:
    print("Running sequential test …\n")
    for cik, url in q_filings.items():
        try:
            bs = get_balance_sheet(cik, url)   # synchronous wrapper
            print(f"✅ {cik} OK")
            #pretty_print(bs)   # uncomment for full object dump
        except Exception as exc:
            print(f"❌ {cik} FAILED → {exc}")

# ---------------------------------------------------------------------------

if __name__ == '__main__':
    freeze_support()   # does nothing on *nix, required on Windows freeze/pyinstaller
    main()




# build_balance_sheet.py 1849635 https://www.sec.gov/Archives/edgar/data/1849635/000114036125018209/0001140361-25-018209-index.html
# build_balance_sheet.py 1687542 https://www.sec.gov/Archives/edgar/data/1687542/000164117225011165/0001641172-25-011165-index.html
# build_balance_sheet.py 1830072 https://www.sec.gov/Archives/edgar/data/1830072/000168316825003710/0001683168-25-003710-index.html
# build_balance_sheet.py 1737523 https://www.sec.gov/Archives/edgar/data/1737523/000147793225003821/0001477932-25-003821-index.html

# build_balance_sheet.py 1820302 https://www.sec.gov/Archives/edgar/data/1820302/000162828025024743/0001628280-25-024743-index.html

# build_balance_sheet.py 1901799 https://www.sec.gov/Archives/edgar/data/1901799/000095017025072051/0000950170-25-072051-index.html


# build_balance_sheet.py 1788230 https://www.sec.gov/Archives/edgar/data/1788230/000178823025000062/0001788230-25-000062-index.html
# build_balance_sheet.py 1865602 https://www.sec.gov/Archives/edgar/data/1865602/000121390025044273/0001213900-25-044273-index.html
# build_balance_sheet.py 1805526 https://www.sec.gov/Archives/edgar/data/1805526/000121390025042977/0001213900-25-042977-index.html
# build_balance_sheet.py 1360442 https://www.sec.gov/Archives/edgar/data/1360442/000109690625000870/0001096906-25-000870-index.html
# build_balance_sheet.py 1922858 https://www.sec.gov/Archives/edgar/data/1922858/000121390025046180/0001213900-25-046180-index.html
# build_balance_sheet.py 1889123 https://www.sec.gov/Archives/edgar/data/1889123/000095017025072818/0000950170-25-072818-index.html
# build_balance_sheet.py 1641398 https://www.sec.gov/Archives/edgar/data/1641398/000121390025044218/0001213900-25-044218-index.html
# build_balance_sheet.py 2022308 https://www.sec.gov/Archives/edgar/data/2022308/000192998025000446/0001929980-25-000446-index.html
# build_balance_sheet.py 1074828 https://www.sec.gov/Archives/edgar/data/1074828/000165495425005607/0001654954-25-005607-index.html
# build_balance_sheet.py 1662684 https://www.sec.gov/Archives/edgar/data/1662684/000141057825001326/0001410578-25-001326-index.html
# build_balance_sheet.py 1050446 https://www.sec.gov/Archives/edgar/data/1050446/000095017025063536/0000950170-25-063536-index.html
# build_balance_sheet.py 1946573 https://www.sec.gov/Archives/edgar/data/1946573/000164117225009328/0001641172-25-009328-index.html
# build_balance_sheet.py 1836875 https://www.sec.gov/Archives/edgar/data/1836875/000183687525000102/0001836875-25-000102-index.html
# build_balance_sheet.py 1784970 https://www.sec.gov/Archives/edgar/data/1784970/000121390025041307/0001213900-25-041307-index.html
# build_balance_sheet.py 1849380 https://www.sec.gov/Archives/edgar/data/1849380/000164117225010321/0001641172-25-010321-index.html
# build_balance_sheet.py 1981535 https://www.sec.gov/Archives/edgar/data/1981535/000164117225010881/0001641172-25-010881-index.html
# build_balance_sheet.py 2015947 https://www.sec.gov/Archives/edgar/data/2015947/000141057825001232/0001410578-25-001232-index.html
# build_balance_sheet.py 1554859 https://www.sec.gov/Archives/edgar/data/1554859/000155485925000020/0001554859-25-000020-index.html
# build_balance_sheet.py 1571934 https://www.sec.gov/Archives/edgar/data/1571934/000141057825001327/0001410578-25-001327-index.html
# build_balance_sheet.py 1853825 https://www.sec.gov/Archives/edgar/data/1853825/000164117225011020/0001641172-25-011020-index.html
# build_balance_sheet.py 1775194 https://www.sec.gov/Archives/edgar/data/1775194/000147793225003866/0001477932-25-003866-index.html
