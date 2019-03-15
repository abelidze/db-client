import sys
from application import Application


def main():
	app = Application(sys.argv)
	return app.exec()

if __name__ == '__main__':
	sys.exit( main() )
