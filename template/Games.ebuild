# Copyright 1999-2004 Gentoo Foundation
# Distributed under the terms of the GNU General Public License v2
# $Header: /cvsroot/abeni/abeni/template/Games.ebuild,v 1.1 2004/08/06 21:03:43 robc Exp $

inherit games

DESCRIPTION=""
HOMEPAGE=""
SRC_URI=""

LICENSE=""
SLOT="0"
KEYWORDS="x86"

IUSE=""
DEPEND=""

src_compile() {
	egamesconf \
		`use_with sdl` \
		`use_with directfb` \
		`use_with ggi` \
		`use_with alsa` \
		|| die "egamesconf failed"
	emake || die "emake failed"
}

src_install() {
	dogamesbin mygame || die "dogamesbin failed"
	insinto "${GAMES_DATADIR}/${PN}"
	doins mygame.stuff || die "doins failed"
	prepgamesdirs
}

pkg_postinst() {
	games_pkg_postinst
	einfo
	einfo "Note: No maps have been installed. If you want them,"
	einfo "      download them from ${HOMEPAGE} and copy them to"
	einfo "      ${GAMES_DATADIR/${PN}"
	einfo
}

