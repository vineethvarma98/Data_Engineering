DELIMITER $$
create TRIGGER trigger_facts
after insert on alerts
for each row
BEGIN
	call load_to_fact_alerts();
END $$
DELIMITER ;

DELIMITER $$
create procedure load_to_fact_alerts()
BEGIN
	declare exit handler for SQLEXCEPTION
    BEGIN
		ROLLBACK;
        SELECT 'Error occurred while loading fact_alerts' AS error_message;
    END;
    
    START transaction;
    
    insert into fact_alerts(
    alert_id,
    created_date,
    resolved_date,
    severity_id,
    status_id,
    source_id,
    resolution_time_minutes,
    updated_timestamp
    )
    select 
    a.alert_id,
    a.created_at,
    a.resolved_date,
    s.severity_id,
    st.status_id,
    so.source_id,
	CASE 
            WHEN a.resolved_at IS NOT NULL 
            THEN TIMESTAMPDIFF(MINUTE, a.created_at, a.resolved_at)
            ELSE NULL
        END  as resolution_time_minutes,
	current_timestamp()
    FROM alerts a
	JOIN dim_severity s ON a.severity = s.severity_name
	JOIN dim_status st ON a.status = st.status_name
	JOIN dim_source so ON a.source_system = so.source_name
    
	WHERE NOT EXISTS (
			SELECT 1 
			FROM fact_alerts f 
			WHERE f.alert_id = a.alert_id
		);

		COMMIT;

		SELECT 'Fact table loaded successfully' AS status_message;

END $$
DELIMITER ;