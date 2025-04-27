# Высчитать лист для пагинации
def get_page_list(current_page: int, total_pages: int) -> list:
    if total_pages <= 7:
        return list(range(1, total_pages + 1))
    
    if current_page <= 4:
        return [1, 2, 3, 4, 5, "ell", total_pages]
    elif current_page >= total_pages - 3:
        return [1, "ell"] + list(range(total_pages-4, total_pages+1))
    else:
        return [1, "ell"] + list(range(current_page-1, current_page+2)) + ["ell", total_pages]
