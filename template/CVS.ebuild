# Copyright 1999-2004 Gentoo Foundation
# Distributed under the terms of the GNU General Public License v2
# $Header: /cvsroot/abeni/abeni/template/CVS.ebuild,v 1.1 2004/08/06 21:03:43 robc Exp $

inherit cvs

ECVS_USER=""
ECVS_SERVER="SERVER:/cvsroot/"
#ECVS_AUTH="ext"
#ECVS_SSH_HOST_KEY=""
#CVS_RSH="ssh"
ECVS_MODULE=""
ECVS_TOP_DIR="${DISTDIR}/cvs-src/${PN}"
S=${WORKDIR}/${ECVS_MODULE}

DESCRIPTION=""
HOMEPAGE=""
SRC_URI=""

LICENSE=""
SLOT="0"
KEYWORDS="~x86"

IUSE=""
DEPEND=""
S=${WORKDIR}/${P}


src_compile() {
	export WANT_AUTOCONF_2_5=1
	sh autogen.sh
	econf || die 'configure failed'
	emake || die 'parallel make failed'
}

src_install() {
	einstall || die 'einstall failed'
}

