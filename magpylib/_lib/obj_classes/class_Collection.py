"""Collection class code"""

import copy
from magpylib._lib.utility import (format_obj_input, check_duplicates,
    only_allowed_src_types)
from magpylib._lib.obj_classes.class_BaseDisplayRepr import BaseDisplayRepr
from magpylib._lib.obj_classes.class_BaseGetBH import BaseGetBH


# ON INTERFACE
class Collection(BaseDisplayRepr, BaseGetBH):
    """
    Group multiple sources in one Collection for common manipulation.

    Operations applied to a Collection are sequentially applied to all sources in the Collection.
    Collections do not allow duplicate sources (will be eliminated automatically).

    Collections have the following dunders defined: __add__, __sub__, __iter__, __getitem__,
    __repr__

    Parameters
    ----------
    sources: source objects, Collections or arbitrary lists thereof
        Ordered list of sources in the Collection.

    Returns
    -------
    Collection object: Collection
    """

    def __init__(self, *sources):

        # inherit
        BaseDisplayRepr.__init__(self)

        self.sources = sources
        self.object_type = 'Collection'


    # sources properties --------------------------------------------
    @property
    def sources(self):
        """ Collection sources attribute getter and setter.
        """
        return self._sources


    @sources.setter
    def sources(self, sources):
        """ Set Collection sources.
        """
        # format input
        src_list = format_obj_input(sources)
        # check and eliminate duplicates
        src_list = check_duplicates(src_list)
        # allow only designated source types in Collection
        src_list = only_allowed_src_types(src_list)
        # set attributes
        self._sources = src_list


    # dunders -------------------------------------------------------
    def __add__(self, source):
        self.add(source)
        return self


    def __sub__(self, source):
        self.remove(source)
        return self


    def __iter__(self):
        yield from self._sources


    def __getitem__(self,i):
        return self._sources[i]


    # methods -------------------------------------------------------
    def add(self,*sources):
        """
        Add arbitrary sources or Collections.

        Parameters
        ----------
        sources: src objects, Collections or arbitrary lists thereof
            Add arbitrary sequences of sources and Collections to the Collection.
            The new sources will be added at the end of self.sources. Duplicates
            will be eliminated.

        Returns
        -------
        self: Collection
        """
        # format input
        src_list = format_obj_input(sources)
        # combine with original src_list
        src_list = self._sources + src_list
        # check and eliminate duplicates
        src_list = check_duplicates(src_list)
        # set attributes
        self._sources = src_list
        return self


    def remove(self,source):
        """
        Remove source from Collection.

        Parameters
        ----------
        source: source object
            Remove the given source from the Collection.

        Returns
        -------
        self: Collection
        """
        self._sources.remove(source)
        return self


    def move(self, displacement, start=-1, increment=False):
        """
        Translates each object in the Collection by the input displacement (can be a path).

        This method uses vector addition to merge the input path given by displacement and the
        existing old path of an object. It keeps the old orientation. If the input path extends
        beyond the old path, the old path will be padded by its last entry before paths are
        added up.

        Parameters
        ----------
        displacement: array_like, shape (3,) or (N,3)
            Displacement vector shape=(3,) or path shape=(N,3) in units of [mm].

        start: int or str, default=-1
            Choose at which index of the original object path, the input path will begin.
            If `start=-1`, inp_path will start at the last old_path position.
            If `start=0`, inp_path will start with the beginning of the old_path.
            If `start=len(old_path)` or `start='append'`, inp_path will be attached to
            the old_path.

        increment: bool, default=False
            If `increment=False`, input displacements are absolute.
            If `increment=True`, input displacements are interpreted as increments of each other.
            For example, an incremental input displacement of `[(2,0,0), (2,0,0), (2,0,0)]`
            corresponds to an absolute input displacement of `[(2,0,0), (4,0,0), (6,0,0)]`.

        Returns
        -------
        self: Collection
        """
        for s in self:
            s.move(displacement, start, increment)
        return self


    def rotate(self, rot, anchor=None, start=-1, increment=False):
        """
        Rotates all objects in the Collection by a given rotation input (can be a path).

        This method applies given rotations to the original orientation. If the input path
        extends beyond the existing path, the old path will be padded by its last entry before paths
        are added up.

        Parameters
        ----------
        rotation: scipy Rotation object
            Rotation to be applied. The rotation object can feature a single rotation
            of shape (3,) or a set of rotations of shape (N,3) that correspond to a path.

        anchor: None, 0 or array_like, shape (3,), default=None
            The axis of rotation passes through the anchor point given in units of [mm].
            By default (`anchor=None`) the object will rotate about its own center.
            `anchor=0` rotates the object about the origin (0,0,0).

        start: int or str, default=-1
            Choose at which index of the original object path, the input path will begin.
            If `start=-1`, inp_path will start at the last old_path position.
            If `start=0`, inp_path will start with the beginning of the old_path.
            If `start=len(old_path)` or `start='append'`, inp_path will be attached to
            the old_path.

        increment: bool, default=False
            If `increment=False`, input rotations are absolute.
            If `increment=True`, input rotations are interpreted as increments of each other.

        Returns
        -------
        self: Collection
        """
        for s in self:
            s.rotate(rot, anchor, start, increment)
        return self


    def rotate_from_angax(self, angle, axis, anchor=None, start=-1, increment=False, degree=True):
        """
        Rotation of all objects in the Collection from angle-axis input.

        This method applies given rotations to the original orientation. If the input path
        extends beyond the existingp path, the oldpath will be padded by its last entry before paths
        are added up.

        Parameters
        ----------
        angle: int/float or array_like with shape (n,) unit [deg] (by default)
            Angle of rotation, or a vector of n angles defining a rotation path in units
            of [deg] (by default).

        axis: str or array_like, shape (3,)
            The direction of the axis of rotation. Input can be a vector of shape (3,)
            or a string 'x', 'y' or 'z' to denote respective directions.

        anchor: None or array_like, shape (3,), default=None, unit [mm]
            The axis of rotation passes through the anchor point given in units of [mm].
            By default (`anchor=None`) the object will rotate about its own center.
            `anchor=0` rotates the object about the origin (0,0,0).

        start: int or str, default=-1
            Choose at which index of the original object path, the input path will begin.
            If `start=-1`, inp_path will start at the last old_path position.
            If `start=0`, inp_path will start with the beginning of the old_path.
            If `start=len(old_path)` or `start='append'`, inp_path will be attached to
            the old_path.

        increment: bool, default=False
            If `increment=False`, input rotations are absolute.
            If `increment=True`, input rotations are interpreted as increments of each other.
            For example, the incremental angles [1,1,1,2,2] correspond to the absolute angles
            [1,2,3,5,7].

        degree: bool, default=True
            By default angle is given in units of [deg]. If degree=False, angle is given
            in units of [rad].

        Returns
        -------
        self: Collection
        """
        for s in self:
            s.rotate_from_angax(angle, axis, anchor, start, increment, degree)
        return self


    def copy(self):
        """
        Returns a copy of the Collection.

        Returns
        -------
        self: Collection
        """
        return copy.copy(self)


    def reset_path(self):
        """
        Reset all object paths to position = (0,0,0) and orientation = unit rotation.

        Returns
        -------
        self: Collection
        """
        for obj in self:
            obj.reset_path()
        return self
