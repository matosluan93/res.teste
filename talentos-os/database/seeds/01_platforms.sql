INSERT INTO platforms (name,slug,color,icon,total_candidates,total_hired,avg_cost_per_hire,conversion_rate,active_jobs) VALUES
('Indique & Ganhe','indicacao','#C9973A','🏆',38,11,4200,7.2,6),
('Gupy','gupy','#4338CA','G',95,9,8800,3.1,12),
('Pandapé','pandape','#FF6B35','P',64,6,9500,2.8,7),
('LinkedIn Jobs','linkedin','#0077B5','in',50,8,14200,4.0,8)
ON CONFLICT (slug) DO NOTHING;
