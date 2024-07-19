# coding: utf-8

from __future__ import absolute_import
from datetime import date, datetime  # noqa: F401

from typing import List, Dict  # noqa: F401

from swagger_server.models.base_model_ import Model
from swagger_server import util


class AreaResYears(Model):
    """NOTE: This class is auto generated by the swagger code generator program.

    Do not edit the class manually.
    """
    def __init__(self, year: str=None):  # noqa: E501
        """AreaResYears - a model defined in Swagger

        :param year: The year of this AreaResYears.  # noqa: E501
        :type year: str
        """
        self.swagger_types = {
            'year': str
        }

        self.attribute_map = {
            'year': 'year'
        }
        self._year = year

    @classmethod
    def from_dict(cls, dikt) -> 'AreaResYears':
        """Returns the dict as a model

        :param dikt: A dict.
        :type: dict
        :return: The AreaRes_years of this AreaResYears.  # noqa: E501
        :rtype: AreaResYears
        """
        return util.deserialize_model(dikt, cls)

    @property
    def year(self) -> str:
        """Gets the year of this AreaResYears.


        :return: The year of this AreaResYears.
        :rtype: str
        """
        return self._year

    @year.setter
    def year(self, year: str):
        """Sets the year of this AreaResYears.


        :param year: The year of this AreaResYears.
        :type year: str
        """

        self._year = year
