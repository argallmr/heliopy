"""
Methods for importing data from Parker Solar Probe.
"""
import astropy.units as u
import pathlib
import urllib.error

from heliopy.data import util


class _PSPDownloader(util.Downloader):
    base_url = 'https://spdf.gsfc.nasa.gov/pub/data/'
    epoch_label = 'Epoch'

    def intervals(self, starttime, endtime):
        return self.intervals_daily(starttime, endtime)

    def download(self, interval):
        url = self.base_url + str(self.local_dir(interval))
        try:
            util._download_remote(url,
                                  self.fname(interval),
                                  self.local_path(interval).parent)
        except urllib.error.HTTPError:
            raise util.NoDataError

    def load_local_file(self, interval):
        local_path = self.local_path(interval)
        cdf = util._load_cdf(local_path)
        return util.cdf2df(
            cdf, index_key=self.epoch_label, badvalues=self.badvalues)


# SWEAP classes/methods
class _SWEAPDownloader(_PSPDownloader):
    badvalues = [-1e31]
    units = {'u/e': u.dimensionless_unscaled}
    # Fill in some missing units
    for i in range(3):
        for j in ['p', 'p1', 'a', '3']:
            units[f'v{j}_fit_SC_{i}'] = u.km / u.s
            units[f'v{j}_fit_SC_uncertainty_{i}'] = u.km / u.s
            units[f'v{j}_fit_RTN_{i}'] = u.km / u.s
            units[f'v{j}_fit_RTN_uncertainty_{i}'] = u.km / u.s
            units[f'v{j}_moment_SC_{i}'] = u.km / u.s
            units[f'v{j}_moment_SC_deltahigh_{i}'] = u.km / u.s
            units[f'v{j}_moment_SC_deltalow_{i}'] = u.km / u.s
            units[f'v{j}_moment_RTN_{i}'] = u.km / u.s
            units[f'v{j}_moment_RTN_deltahigh_{i}'] = u.km / u.s
            units[f'v{j}_moment_RTN_deltalow_{i}'] = u.km / u.s

    def __init__(self, level):
        assert level in (2, 3)
        self.level = level

    def local_dir(self, interval):
        year = interval.start.strftime('%Y')
        return (pathlib.Path('psp') / 'sweap' / 'spc' /
                f'l{self.level}' / f'l{self.level}i' / year)

    def fname(self, interval):
        datestr = interval.start.strftime('%Y%m%d')
        return f'psp_swp_spc_l{self.level}i_{datestr}_v01.cdf'


def sweap_spc_l2(starttime, endtime):
    """
    SWEAP SPC proton and alpha particle moments and fits.
    """
    dl = _SWEAPDownloader(level=2)
    return dl.load(starttime, endtime)


def sweap_spc_l3(starttime, endtime):
    """
    SWEAP SPC proton and alpha particle moments and fits.
    """
    dl = _SWEAPDownloader(level=3)
    return dl.load(starttime, endtime)


# FIELDS classes/methods
class _FIELDSDownloader(_PSPDownloader):
    badvalues = None


class _FIELDSmag_RTN_1min_Downloader(_FIELDSDownloader):
    epoch_label = 'epoch_mag_RTN_1min'

    def local_dir(self, interval):
        year = interval.start.strftime('%Y')
        return pathlib.Path('psp') / 'fields' / 'l2' / 'mag_rtn_1min' / year

    def fname(self, interval):
        datestr = interval.start.strftime('%Y%m%d')
        return f'psp_fld_l2_mag_rtn_1min_{datestr}_v01.cdf'


def fields_mag_rtn_1min(starttime, endtime):
    """
    1 minute averaged magnetic field data.
    """
    dl = _FIELDSmag_RTN_1min_Downloader()
    return dl.load(starttime, endtime)
