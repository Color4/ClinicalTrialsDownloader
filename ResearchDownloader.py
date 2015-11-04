import requests
import os
import zipfile
import errno


BASE_PATH = os.path.dirname(
    os.path.abspath(__file__)
)

DOWNLOAD_PATH = BASE_PATH + '/downloads/'
SEARCH_PARAMETERS_FILE = BASE_PATH + '/params.txt'


class ResearchDownloader(object):
    """
    This collects research from clinicaltrials.gov as specified
    by the criteria designated within the adjacent text file
    params.txt. For instructions on how to format this file,
    please see README.md
    """
    search_criteria = []
    relative_download_dirs = []

    def __init__(self):
        print('> Gathering search criteria...')
        self.get_search_criteria()
        self.make_sure_path_exists(DOWNLOAD_PATH)
        for criteria in self.search_criteria:
            self.download_research(criteria)

    def get_search_criteria(self):
        """
        Collects search criteria from local file params.txt
        """
        try:
            with open(SEARCH_PARAMETERS_FILE, 'r+') as f:
                    for line in f:
                        print(
                            '> Adding terms to queue: "{}"'
                            .format(line)
                        )
                        full_terms = ''
                        search_terms = line.split(' ')

                        for idx, term in enumerate(search_terms):
                            if idx != (len(search_terms) - 1):
                                full_terms += term + '+'
                            else:
                                full_terms += term

                        self.search_criteria.append(full_terms)
        except OSError:
            raise OSError(
                """
                Search parameters file params.txt doesn't seem to
                be present in the root directory of this program. Have
                you read the README.md and created this file accordingly?
                Also, make sure permissions are set for reading and
                writing throughout this project's directory.
                """
            )

    def download_research(self, criteria):
        """
        Downloads a .zip file full of XML files containing
        research relevant to the given criteria, then extracts
        the contents to the proper destination in /downloads/
        in the project folder.
        """
        full_download_url = self.get_download_url(criteria)
        full_destination = \
            DOWNLOAD_PATH + criteria.replace('+', '_') + '_research.zip'

        print(
            '> Downloading archive of results for parameters "{}"'
            .format(criteria)
        )

        self.download_file(full_download_url, full_destination)

        print(
            '> Extracting contents of archive of results for parameters "{}"'
            .format(criteria)
        )

        downloaded_dir = self.extract_zip_contents(full_destination)

        print(
            '> Results for parameters "{}" stored in /downloads/{}/'
            .format(criteria, downloaded_dir)
        )

        self.relative_download_dirs.append(
            downloaded_dir
        )

        os.remove(full_destination)

    def get_download_url(self, criteria):
        """
        Creates the download url for the .zip archive from
        the given criteria.
        """
        prepended_url_part = 'https://clinicaltrials.gov/ct2/results/' +\
                             'download?down_flds=shown&down_fmt=plain&term='
        appended_url_part = '&show_down=Y&down_typ=results&down_stds=all'
        return prepended_url_part + criteria + appended_url_part

    def download_file(self, url, destination):
        """
        Downloads and saves a .zip archive file from the
        given url to the given destination.
        """
        download_stream = requests.get(url, stream=True)

        try:
            with open(destination, 'wb') as f:
                for chunk in download_stream.iter_content(chunk_size=1024):
                    if chunk:
                        f.write(chunk)
        except IOError:
            raise IOError('Could not write downloaded research to disk.')

    def extract_zip_contents(self, path):
        """
        Extracts the contents of the .zip archive at the
        given location to a folder named accordingly in the
        /downloads/ folder.
        """
        try:
            with open(path, 'rb') as saved_zip:
                DESTINATION_DIR = path.replace('.zip', '/')
                self.make_sure_path_exists(DESTINATION_DIR)

                zf = zipfile.ZipFile(saved_zip)
                zf.extractall(DESTINATION_DIR)

                return DESTINATION_DIR.split('/')[-2]
        except IOError:
            raise IOError(
                'ERROR: Could not extract files from .zip research archive.'
            )

    def make_sure_path_exists(self, path):
        """
        Create directory from path if it doesn't exist.
        Credit to 'Heikki Toivonon' and 'Bengt' on
        StackOverflow.
        http://stackoverflow.com/questions/273192/in-python-check-if-a-directory-exists-and-create-it-if-necessary
        """
        try:
            os.makedirs(path)
        except OSError as exception:
            if exception.errno != errno.EEXIST:
                raise
