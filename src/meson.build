subdir('resources')

pkgdatadir = join_paths(get_option('prefix'), get_option('datadir'), meson.project_name())
moduledir = join_paths(pkgdatadir, 'telex')

python3 = import('python3')

conf = configuration_data()
conf.set('PYTHON', python3.find_python().path())
conf.set('VERSION', meson.project_version())
conf.set('localedir', join_paths(get_option('prefix'), get_option('localedir')))
conf.set('pkgdatadir', pkgdatadir)

configure_file(
  input: 'telex.in',
  output: 'telex',
  configuration: conf,
  install: true,
  install_dir: get_option('bindir')
)

telex_sources = [
  '__init__.py',
  'client.py',
  'settings.py',
  'main.py',
  'window.py',
  'preferences_window.py',
  'contacts_dialog.py',
  'widgets_old.py',
  'letter_avatar.py',
  'widget_avatar.py',
  'widget_message.py',
]

install_data(telex_sources, install_dir: moduledir)
