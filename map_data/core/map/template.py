"""
Module to create a template of a map.
"""
from __future__ import annotations

from enum import Enum
from typing import Collection, Iterable

from map_data.core.utils import snake_case_to_camel_case

# ======================================================================================================================
# Constants for the map template
# ======================================================================================================================

MIN_ZOOM = 0
MAX_ZOOM = 18

# ======================================================================================================================
# Enums
# ======================================================================================================================

class Tile(Enum):
    """Defines the different tiles that can be used."""
    OPEN_STREET_MAP     = "openstreetmap", False
    CARTO_DB_POSITRON   = "cartodbpositron", False
    PLAN_IGN            = "plan_ign", True

    def __init__(self, tile_name : str, is_custom : bool):
        self.tile_name = tile_name
        self.is_custom = is_custom
# End class Tile

# ======================================================================================================================
# Classes
# ======================================================================================================================

class Style:
    """Represent a style of the data.

    A style can either be applied to a layer or to an element which match a given property.
    """

    default_style = {
        "stroke"       : True,
        "color"        : "#3388ff",
        "weight"       : 3,
        "opacity"      : 1,
        "line_cap"     : 'round',
        "line_join"    : 'round',
        "dash_array"   : None,
        "dash_offset"  : None,
        "fill"         : True,
        "fill_color"   : "#3388ff",
        "fill_opacity" : 0.2,
        "fill_rule"    : 'evenodd',
    }

    # ------------------------------------------------------------------------------------------------------------------
    # Magic Methods
    # ------------------------------------------------------------------------------------------------------------------

    def __init__(self, **kwargs):

        # Style properties
        self.stroke       : bool | None        = kwargs.get("stroke", None)
        self.color        : str | None         = kwargs.get("color", None)
        self.weight       : float | int | None = kwargs.get("weight", None)
        self.opacity      : float | int | None = kwargs.get("opacity", None)
        self.line_cap     : str | None         = kwargs.get("line_cap", None)
        self.line_join    : str | None         = kwargs.get("line_join", None)
        self.dash_array   : str | None         = kwargs.get("dash_array", None)
        self.dash_offset  : str | None         = kwargs.get("dash_offset", None)
        self.fill         : bool | None        = kwargs.get("fill", None)
        self.fill_color   : str | None         = kwargs.get("fill_color", None)
        self.fill_opacity : int | float | None = kwargs.get("fill_opacity", None)
        self.fill_rule    : str | None         = kwargs.get("fill_rule", None)


        self._properties_styles : list[tuple[str, str, Style]] = list()


        if kwargs.get("fill_with_default") is True:
            self.__fill_defaults()
    # End def __init__

    def __str__(self):
        attrs = ", ".join(f"{k}={v!r}" for k, v in self.__dict__.items() if v is not None and not k.startswith('_'))
        return f"{self.__class__.__name__}({attrs})"
    # End def __str__

    def __repr__(self):
        return "{class_}@{id:x}({attrs})".format(
            class_=self.__class__.__name__,
            id=id(self),
            attrs=", ".join("{}={!r}".format(k, v) for k, v in self.__dict__.items()),
        )
    # End def __repr__

    # ------------------------------------------------------------------------------------------------------------------
    # Setters
    # ------------------------------------------------------------------------------------------------------------------

    def add_property_style(self, property_name : str, property_value : str, style : Style):
        """Add a property style."""
        self._properties_styles.append((property_name, property_value, style))
    # End def add_property_style

    # ------------------------------------------------------------------------------------------------------------------
    # Methods
    # ------------------------------------------------------------------------------------------------------------------

    def function_style(self, x : dict) -> dict:
        """Function used to style the data.

        Args:
            x (dict): The data to style.
        """

        attributes = [
            "stroke", "color", "weight", "opacity", "line_cap",
            "dash_array", "dash_offset", "fill", "fill_color",
            "fill_opacity", "fill_rule"
        ]

        rstyle = {}
        # Get the style for the layer
        for attr in attributes:
            value = getattr(self, attr)
            if value is not None:
                rstyle[snake_case_to_camel_case(attr)] = value

        # For each property style, check if the property value matches the value of the property in the data
        # If it does, add the style to the style
        for property_name, property_value, style in self._properties_styles:
            try:
                if x["properties"].get(property_name, None) == property_value:
                    for attr in attributes:
                        value = getattr(style, attr)
                        if value is not None:
                            rstyle[snake_case_to_camel_case(attr)] = value
            except Exception:
                pass

        return rstyle
    # End def function_style

    def validate(self):
        """Validate the style."""
    # End def validate

    # ------------------------------------------------------------------------------------------------------------------
    # Private methods
    # ------------------------------------------------------------------------------------------------------------------

    def __fill_defaults(self):
        """Fills the style with the default values."""
        for attr, default_value in Style.default_style.items():
            if getattr(self, attr) is None:
                setattr(self, attr, default_value)
    # End def __fill_defaults
# End class Style

class Layer:
    """Represents a map layer.

    A map layer is a layer of data that can be shown or hidden on the map.
    The map layer to load is defined by its name in the database.
    """
    def __init__(
            self,
            name : str,
            map_layer: str,
            style : Style | None = None,
            highlight : Style | None = None,
            show_on_startup : bool = True
    ) -> None:
        self.name            : str          = name
        self.map_layer       : str          = map_layer
        self.style           : Style | None = style
        self.highlight       : Style | None = highlight
        self.show_on_startup : bool         = show_on_startup
    # End def __init__

    # ------------------------------------------------------------------------------------------------------------------
    # Methods
    # ------------------------------------------------------------------------------------------------------------------

    def validate(self):
        """Validate the layer."""
        # Validate that the zoom start is valid
        if self.style is not None:
            self.style.validate()
        if self.highlight is not None:
            self.highlight.validate()
# End class Layer


class FeatureGroup:
    """Represents a map feature group.

    A feature group is a group of features that can be shown or hidden on the map.
    It may contain multiple layers, markers, etc.
    """

    def __init__(
            self,
            name : str | None = None,
            show_on_startup : bool = True,
            layers : Iterable | Collection | None = None
    ) -> None:
        self.name : str | None = name
        self.show_on_startup : bool = show_on_startup
        self.__layers : list[Layer] = []

        if layers is None:
            return
        if not isinstance(layers, (Collection, Iterable)):
            raise ValueError(f"Expected 'layers' to be a `Collection` or an `Iterable`, not `{type(layers)}`")

        for i, layer in enumerate(layers):
            if not isinstance(layer, Layer):
                raise ValueError(f"Expected layers@{i} to be a `Layer`, not `{type(layer)}`")
            self.add_layer(layer)
    # End def __init__

    # ==================================================================================================================
    # Getters
    # ==================================================================================================================

    def get_layers(self) -> list[Layer]:
        """Get the layers."""
        return self.__layers
    # End def get_layers

    def get_layer(self, name : str, raise_if_not_exists : bool = False) -> Layer | None:
        """Get a layer from its name."""
        try:
            return next((l for l in self.__layers if l.name == name))
        except StopIteration:
            if raise_if_not_exists is True:
                raise ValueError(f"Layer '{name}' does not exist in feature group")
            return None
    # End def get_layer

    # ==================================================================================================================
    # Setters
    # ==================================================================================================================

    def add_layer(self, layer: Layer):
        """Add a layer to the template."""
        # Ensure that a layer with the same name does not already exist
        already_exists = False if next((l for l in self.__layers if l.name == layer.name), None) is None else True
        if already_exists:
            raise ValueError(f"FeatureGroup '{layer.name}' already exists in the template")
        self.__layers.append(layer)
    # End def add_layer
# End class FeatureGroup


class MapTemplate:
    def __init__(self):
        self.name : str = ""
        self.tile : Tile = Tile.OPEN_STREET_MAP
        self.zoom_start : int | None = None
        self.enable_layer_control = True
        self.enable_zoom_control = True

        # Private properties
        self.__feature_groups: list[FeatureGroup] = list()
    # End def __init__

    # ------------------------------------------------------------------------------------------------------------------
    # Magic Methods
    # ------------------------------------------------------------------------------------------------------------------

    def __str__(self):
        return "MapTemplate:{}".format(self.__hash__() if self.name.strip() in ("", None) else self.name)
    # End def __str__

    def __repr__(self):
        repr_str = "MapTemplate("
        repr_str += f"tile={repr(self.tile)}, "
        repr_str += f"zoom_start={self.zoom_start}, "
        repr_str += f"layer_control={self.enable_layer_control}, "
        repr_str += f"enable_zoom_control={self.enable_layer_control}, "
        repr_str += "feature_groups=["
        for idx, fg in self.__feature_groups[:-1]:
            repr_str += f"{repr(fg)}, "
        repr_str += f"{repr(self.__feature_groups[-1])}]"
        repr_str += ")"

        return repr_str
    # End def __repr__

    # ------------------------------------------------------------------------------------------------------------------
    # Getters
    # ------------------------------------------------------------------------------------------------------------------

    def get_feature_groups(self) -> list[FeatureGroup]:
        """Get the layers."""
        return self.__feature_groups
    # End def get_layers

    def get_feature_group(self, name : str) -> FeatureGroup:
        """Get a layer from its name."""
        return next((l for l in self.__feature_groups if l.name == name), None)
    # End def get_layer

    # ------------------------------------------------------------------------------------------------------------------
    # Setters
    # ------------------------------------------------------------------------------------------------------------------

    def add_feature_group(self, feature_group: FeatureGroup):
        """Add a layer to the template."""
        # Ensure that a layer with the same name does not already exist
        already_exists = False if next((l for l in self.__feature_groups if l.name == feature_group.name), None) is None else True
        if already_exists:
            raise ValueError(f"FeatureGroup '{feature_group.name}' already exists in the template")

        self.__feature_groups.append(feature_group)
    # End def add_layer

    # ------------------------------------------------------------------------------------------------------------------
    # Methods
    # ------------------------------------------------------------------------------------------------------------------

    def remove_feature_group(self, fg_or_name : FeatureGroup | str, raise_if_not_exists : bool = False):
        """Remove a layer from the template."""
        # Get the layer
        try:
            if isinstance(fg_or_name, str):
                layer = next((l for l in self.__feature_groups if l.name == fg_or_name))
            elif isinstance(fg_or_name, FeatureGroup):
                layer = next((l for l in self.__feature_groups if l is fg_or_name))
            else:
                raise TypeError(f"'fg_or_name' must be of type 'FeatureGroup' or 'str', not {type(fg_or_name)})")
        except StopIteration:
            if raise_if_not_exists:
                raise ValueError("Feature group '{}' does not exist in the template".format(
                    fg_or_name if isinstance(fg_or_name, str) else fg_or_name.name
                ))
            else:
                return

        self.__feature_groups.remove(layer)
    # End def remove_layer

    def validate(self):
        """Validate the template."""
        # Validate that the zoom start is valid
        if self.zoom_start is not None and (self.zoom_start < MIN_ZOOM or self.zoom_start > MAX_ZOOM):
            raise ValueError(f"Zoom start must be between {MIN_ZOOM} and {MAX_ZOOM} (got {self.zoom_start})")
# End class MapTemplate

