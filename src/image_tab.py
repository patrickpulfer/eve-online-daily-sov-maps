class ImageTab:
    """Class to handle image tabs with zoom functionality"""
    
    def __init__(self, filepath):
        # Create container box
        self.box = Gtk.Box.new(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        self.box.set_hexpand(True)
        self.box.set_vexpand(True)

        # Create picture widget
        self.picture = Gtk.Picture.new_for_file(Gio.File.new_for_path(filepath))
        self.picture.set_can_shrink(True)
        self.picture.set_content_fit(Gtk.ContentFit.CONTAIN)
        self.picture.set_hexpand(True)
        self.picture.set_vexpand(True)

        # Store initial size for zooming
        texture = self.picture.get_paintable()
        if texture:
            self.picture.original_width = texture.get_intrinsic_width()
            self.picture.original_height = texture.get_intrinsic_height()
            self.picture.scale = 1.0

        # Create scrolled window
        self.scroll = Gtk.ScrolledWindow()
        self.scroll.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        self.scroll.set_hexpand(True)
        self.scroll.set_vexpand(True)
        self.scroll.set_child(self.box)
        self.scroll.set_kinetic_scrolling(True)
        self.scroll.set_overlay_scrolling(True)

        # Add picture to box
        self.box.append(self.picture)

    def zoom_in(self, button):
        """Zoom in the picture and maintain view center"""
        texture = self.picture.get_paintable()
        if texture and hasattr(self.picture, 'scale'):
            self._zoom(self.picture.scale * 1.2)

    def zoom_out(self, button):
        """Zoom out the picture and maintain view center"""
        texture = self.picture.get_paintable()
        if texture and hasattr(self.picture, 'scale'):
            self._zoom(self.picture.scale / 1.2)

    def zoom_fit(self, button):
        """Reset zoom to fit window"""
        texture = self.picture.get_paintable()
        if texture:
            self.picture.scale = 1.0
            self.picture.set_size_request(-1, -1)

    def _zoom(self, new_scale):
        """Internal method to handle zooming"""
        # Get the scrolled window adjustments
        hadj = self.scroll.get_hadjustment()
        vadj = self.scroll.get_vadjustment()
        
        # Calculate view center as percentage
        rel_x = (hadj.get_value() + hadj.get_page_size() / 2) / max(1, hadj.get_upper())
        rel_y = (vadj.get_value() + vadj.get_page_size() / 2) / max(1, vadj.get_upper())
        
        # Apply zoom with limits
        self.picture.scale = max(min(new_scale, 5.0), 0.1)
        new_width = int(self.picture.original_width * self.picture.scale)
        new_height = int(self.picture.original_height * self.picture.scale)
        self.picture.set_size_request(new_width, new_height)
        
        # Update scroll position after resize
        def update_scroll():
            new_upper_x = hadj.get_upper()
            new_upper_y = vadj.get_upper()
            
            hadj.set_value(max(0, min(
                new_upper_x * rel_x - hadj.get_page_size() / 2,
                new_upper_x - hadj.get_page_size()
            )))
            vadj.set_value(max(0, min(
                new_upper_y * rel_y - vadj.get_page_size() / 2,
                new_upper_y - vadj.get_page_size()
            )))
            return False
        
        GLib.timeout_add(50, update_scroll)