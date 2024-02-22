import pandas as pd

# Citirea datelor din fișierul CSV
movie_data = pd.read_csv("database/movie_data.csv")


# # Eliminarea coloanelor nedorite
# columns_to_drop = ['adult', 'budget', 'revenue']
# movie_data.drop(columns=columns_to_drop, inplace=True)

# # Reducerea numărului de actori la 3
# movie_data['cast'] = movie_data['cast'].apply(lambda x: eval(x)[:3] if pd.notnull(x) else [])

# # Păstrarea primului rând cu denumirile coloanelor
# header = movie_data.iloc[:1]

# # Eliminarea primului rând pentru a lucra doar cu datele
# movie_data = movie_data.iloc[1:]

# # Amestecarea aleatorie a datelor
# movie_data = movie_data.sample(frac=1)

# # Păstrarea primelor 10.000 de rânduri
# movie_data = movie_data.head(10000)

# # Readaugarea primului rând la începutul datelor
# movie_data = pd.concat([header, movie_data])

movie_data_f = movie_data[movie_data['vote_average'] > 8.9]

movie_data = movie_data.drop(movie_data_f.index)

# Salvarea datelor într-un nou fișier CSV
movie_data.to_csv("database/movie_data.csv", index=False)


