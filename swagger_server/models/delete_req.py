# coding: utf-8

from __future__ import absolute_import
from datetime import date, datetime  # noqa: F401

from typing import List, Dict  # noqa: F401

from swagger_server.models.base_model_ import Model
from swagger_server import util


class DeleteReq(Model):
    """NOTE: This class is auto generated by the swagger code generator program.

    Do not edit the class manually.
    """
    def __init__(self, ids: List[int]=None):  # noqa: E501
        """DeleteReq - a model defined in Swagger

        :param ids: The ids of this DeleteReq.  # noqa: E501
        :type ids: List[int]
        """
        self.swagger_types = {
            'ids': List[int]
        }

        self.attribute_map = {
            'ids': 'ids'
        }
        self._ids = ids

    @classmethod
    def from_dict(cls, dikt) -> 'DeleteReq':
        """Returns the dict as a model

        :param dikt: A dict.
        :type: dict
        :return: The DeleteReq of this DeleteReq.  # noqa: E501
        :rtype: DeleteReq
        """
        return util.deserialize_model(dikt, cls)

    @property
    def ids(self) -> List[int]:
        """Gets the ids of this DeleteReq.


        :return: The ids of this DeleteReq.
        :rtype: List[int]
        """
        return self._ids

    @ids.setter
    def ids(self, ids: List[int]):
        """Sets the ids of this DeleteReq.


        :param ids: The ids of this DeleteReq.
        :type ids: List[int]
        """

        self._ids = ids
