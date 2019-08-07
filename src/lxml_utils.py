

def get_el_text_by_css(el, css):
    el = get_el_by_css(el, css)
    return el.text_content() if el is not None else ""


def get_el_by_css(el, css):
    if el != None:
        elems = el.cssselect(css)
        if(elems != None and len(elems) > 0):
            return elems[0]


def get_el_attr_by_css(el, css, attribute):
    el = get_el_by_css(el, css)
    return el.get(attribute) if el is not None else None