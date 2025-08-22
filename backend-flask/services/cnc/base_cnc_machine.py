from services.cnc.cnc_models import LocationModel


class BaseCncMachine:
    """Base class for common CNC machine functionality"""
    
    def __init__(self):
        self._port = None
        self._abort_requested = False
    
    def get_port(self):
        """Get the CNC machine port"""
        return self._port

    @staticmethod
    def _is_at(x, current_x):
        """Check if coordinate matches current position with tolerance
        
        Uses 0.01mm tolerance to match 2 decimal place precision.
        """
        if x is None:
            return True
        else:
            # Use tolerance of 0.01mm for position comparison
            return abs(abs(x) - abs(current_x)) < 0.01

    def is_at(self, x, y, z):
        """Check if machine is at specified coordinates"""
        pos = self.current_pos()
        if not pos:
            return False
        return self._is_at(x, pos.x) \
               and self._is_at(y, pos.y) \
               and self._is_at(z, pos.z)

    def is_at_location(self, location: LocationModel):
        """Check if machine is at specified LocationModel position"""
        x = location.x
        y = location.y
        z = location.z
        return self.is_at(x, y, z)

    def parse_coordinates(self, x, y, z, feed_rate):
        """Parse coordinates into G-code parameter string with proper formatting
        
        Uses 2 decimal places (0.01mm precision) for coordinates for optimal
        balance between precision and compatibility with all CNC controllers.
        """
        parts = []
        if x is not None:
            parts.append(f"X{x:.2f}")  # 2 decimal places for 0.01mm precision
        if y is not None:
            parts.append(f"Y{y:.2f}")  # 2 decimal places for 0.01mm precision
        if z is not None:
            parts.append(f"Z{z:.2f}")  # 2 decimal places for 0.01mm precision
        if feed_rate is not None:
            parts.append(f"F{int(feed_rate)}")
        return " ".join(parts)

    def create_location_model(self, pos_tuple):
        """Create LocationModel from position tuple - centralized pattern"""
        if not pos_tuple:
            return None
        return LocationModel(
            uid=None, 
            axis_uid=None, 
            degree_in_step=None, 
            feedrate=None, 
            name=None, 
            x=pos_tuple[0],
            y=pos_tuple[1], 
            z=pos_tuple[2]
        )

    def standard_disconnect_cleanup(self, connection_obj_name):
        """Standard disconnect cleanup pattern"""
        connection_obj = getattr(self, connection_obj_name)
        if connection_obj:
            try:
                self._abort_requested = False
                connection_obj.soft_reset()
                connection_obj.disconnect()
                setattr(self, connection_obj_name, None)
            except Exception as e:
                setattr(self, connection_obj_name, None)
                raise e

    # Abstract methods that must be implemented by subclasses
    def current_pos(self):
        """Get current position - must be implemented by subclass"""
        raise NotImplementedError("Subclass must implement current_pos()")
    
    def send(self, command: str):
        """Send command - must be implemented by subclass"""
        raise NotImplementedError("Subclass must implement send()")
    
    def disconnect(self):
        """Disconnect - must be implemented by subclass"""
        raise NotImplementedError("Subclass must implement disconnect()")