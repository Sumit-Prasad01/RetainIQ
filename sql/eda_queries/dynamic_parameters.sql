-- Q3: Customers above min tenure, below max balance, below max product count
SELECT
    a.customerid,
    a.tenure,
    a.balance,
    a.numproducts,
    d.churned
FROM public.account a
JOIN public.demographic d ON d.customerid = a.customerid
WHERE
    a.tenure > %(min_tenure)s
    AND a.balance < %(max_balance)s
    AND a.numproducts < %(max_product)s;