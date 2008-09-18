#!/usr/bin/python
# TODO: this was in progress. never finished it or made it test case format
import gtk

class showuri_test:
	def __init__(self):
		self.about = None	# about dialog
		gtk.about_dialog_set_url_hook(self.show_uri)

		# about menu
		self.menu = gtk.Menu()
		about = gtk.ImageMenuItem(gtk.STOCK_ABOUT)
		about.connect('activate', self.about_activate)
		about.show()
		self.menu.append(about)
                quit = gtk.ImageMenuItem(gtk.STOCK_QUIT)
                quit.connect('activate', gtk.main_quit)
                quit.show()
                self.menu.append(quit)
		self.menu.popup(None, None, None, 1, 1)

		gtk.main()

	def show_uri(self, dialog, link):
		"""show a uri."""
		# XXX: gtk.gdk.CURRENT_TIME doesn't exist!
		gtk.show_uri(dialog.get_screen(), link, 0)


	def run():
		self.show_uri(self.menu, 'http://bugzilla.gnome.org/')


	def about_activate(self, widget):
		"""show an about dialog."""
		if self.about is not None:
			self.about.present()
			return False

		self.about = gtk.AboutDialog()
		self.about.set_program_name('bugzilla test')
		self.about.set_authors('james')
		self.about.set_comments('test case for this bug')
		self.about.set_website('http://bugzilla.gnome.org/')
		self.about.set_website_label('Bugzilla Website')
		self.about.run()
		self.about.destroy()
		self.about = None


x = showuri_test()
x.run()

