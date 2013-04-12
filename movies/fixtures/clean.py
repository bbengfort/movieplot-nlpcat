
if __name__ == "__main__":

    with open("title_list.orig") as titles:
        for title in titles:
            title = title.strip()
            if title:
                if ", The" in title:
                    title = "The " + title.replace(", The", "")
                if ", An" in title:
                    title = "An " + title.replace(", An", "")
                if ", A" in title:
                    title = "A " + title.replace(", A", "")
                print title
