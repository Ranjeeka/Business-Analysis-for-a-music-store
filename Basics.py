#!/usr/bin/env python
# coding: utf-8

# In[1]:


get_ipython().run_cell_magic('capture', '', '%load_ext sql\n%sql sqlite:///chinook.db')


# ## CHINOOK RECORDS DATABASE - A BUSINESS ANALYSIS REPORT ##

# The record store is signing a deal with a new record label and we are tasked with answering some important questions that will help the business get answers to make good decisions to acquire most profit.

# In[2]:


get_ipython().run_cell_magic('sql', '', 'SELECT\n    name,\n    type\nFROM sqlite_master\nWHERE type IN ("table","view");')


#  ### Genres that sell the best in the USA among the prospective new artists that make music in - Hip-Hop, Punk, Pop, Blues ###

# In[3]:


get_ipython().run_cell_magic('sql', '', 'WITH track_genre AS\n(\n  SELECT i.quantity,\n         i.track_id,\n         g.name AS genre_name,\n         t.album_id\n    FROM invoice_line i\n    INNER JOIN track t ON t.track_id = i.track_id\n    INNER JOIN genre g ON g.genre_id = t.genre_id\n    GROUP BY i.track_id\n)\nSELECT genre_name,\n       SUM(quantity) total_sold \n       FROM track_genre \n        wHERE genre_name like "%Hip Hop%" or \n        genre_name like "%Punk%" or \n        genre_name = "Pop" or\n        genre_name = "Blues"\n        GROUP BY genre_name\n        ORDER BY total_sold DESC\n        ;\n       ')


# From the list of provided artists and their genres, chinook records should purchase music from: 
# -  **Red Tone (Punk) is our top choice**, 
# -  **SLIM JIM BITES, a Blues artist** 
# -  **Meteor and the girls, pop artists**

# In[4]:


get_ipython().run_cell_magic('sql', '', 'WITH support_sales AS\n(\nSELECT  CAST(SUM(i.total) AS INTEGER) total_sales_amount,\n        MIN(i.total) highest_val,\n        c.support_rep_id,\n        e.first_name || " " || e.last_name sales_name\n        FROM invoice i\n    LEFT JOIN customer c ON c.customer_id = i.customer_id\n    LEFT JOIN employee e ON e.employee_id = c.support_rep_id\n    GROUP BY support_rep_id\n)\nSELECT sales_name, total_sales_amount, support_rep_id\nFROM support_sales\nORDER BY total_sales_amount DESC;')


# Jane Peacock has the highest sales record amounting to 1731 dollars. The least sales record is held by Steve Johnson.

# In[5]:


get_ipython().run_cell_magic('sql', '', 'SELECT *\n\nFROM employee\nWHERE employee_id = 3 or\nemployee_id = 4 or\nemployee_id = 5\n;')


# A quick look-up at the employee table tells us that the least performing salesman with **Steve Johnson has a phone number with area code in Alberta, Calgary** whereas the **other two agents have a number from the Calgary area** which is where the office is. Steve Johnson seems to be **working remotely** which could explain his lower sales numbers.

# ### Analyzing sales data from different countries ###
# 
# We are going to look at sales by country and average order value by country to determine:
# - Country with the most overall sales.
# - Country with the highest average order value.
# 
# Some countries have only 1 customer, we will label those countries as other.

# In[6]:


get_ipython().run_cell_magic('sql', '', "DROP VIEW IF EXISTS cust_count;\nCREATE VIEW cust_count AS\n\nSELECT \nCOUNT(customer_id) ct,\ncountry,\n\nCASE \nWHEN COUNT(customer_id)= 1 THEN 'other'\nEND AS sort\n\nFROM customer\nGROUP BY country\nORDER BY sort;\n\n \n\nSELECT *\n\nFROM cust_count\n\n;")


# In[7]:


get_ipython().run_cell_magic('sql', '', 'DROP VIEW IF EXISTS avg_order_val;\nCREATE VIEW avg_order_val AS\n\nSELECT \ncountry,\navg(total) av_ord_val\nFROM customer c\nINNER JOIN \n(\n    SELECT invoice_id,\n    total,\n    customer_id ci\n    FROM invoice i\n    GROUP BY invoice_id)  ON ci = c.customer_id\nGROUP BY country;')


# In[8]:


get_ipython().run_cell_magic('sql', '', 'SELECT c.country, \nct customer_count,\nSUM(tot) total_sales,\nAVG(tots) avg_sales_customer,\nav.av_ord_val,\ncc.sort\nFROM customer c\nINNER JOIN (\n    SELECT SUM(i.total) tot,\n    i.total tots,\n    customer_id id_c\n    FROM invoice i\n    GROUP BY customer_id )\nON id_c = c.customer_id\nINNER JOIN cust_count cc ON cc.country = c.country\nINNER JOIN avg_order_val av ON av.country = c.country\nGROUP BY c.country\nORDER BY cc.sort, total_sales DESC;')


# **According our findings**
# - USA has the highest total sales amounting to USD 1040 with 13 customers
# - Czech Republic has the highest average order value at USD 9.1 
# 

# ### Calculating number of invoices with album sales ###
# 
# The company wants to know if customer tend to purchase whole albums or just a few tracks from an album. To answer that question we take a look at the invoice_line and track tables. We will calculate:
# 
# - Number of invoices
# - total number of invoices with album purchases

# In[89]:


get_ipython().run_cell_magic('sql', '', 'WITH invoice_album AS\n\n(\n    SELECT il.invoice_id, \n         il.track_id, \n         t.album_id \nFROM invoice_line il\nINNER JOIN (SELECT * FROM track) t ON t.track_id = il.track_id\n),\n\ntracks_count AS\n(\nSelect invoice_id,\n       ia.album_id,\n       COUNT(ia.album_id) tracks_invoice,\n        tracks_album\n    FROM invoice_album ia\n    LEFT JOIN \n    ( SELECT COUNT(t.track_id) tracks_album, album_id AS tai\n     FROM track t\n     GROUP BY tai) ON tai= ia.album_id\nGROUP BY invoice_id, ia.album_id\n), final_count AS\n(\nSELECT *, \nCASE\nWHEN tracks_invoice = tracks_album\nTHEN 1\nELSE 0\nEND AS type_invoice\nFROM tracks_count\nGROUP BY invoice_id\nHAVING tracks_album > 2\n)\n\nSelect MAX(invoice_id) Total_invoices, CAST(SUM(type_invoice) AS FLOAT)/614  from final_count;')


# Around 18% of the invoices are album purchases. Based on our findings, we recomment Chinook Company to avoid full album purchases and purchase only tracks from Albums.
