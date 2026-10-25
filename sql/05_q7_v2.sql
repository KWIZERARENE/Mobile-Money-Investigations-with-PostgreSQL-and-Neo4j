-- ============================================================================
-- 05_q7_v2.sql: Optimized Shortest Path Traversal Function (q7_v2)
-- ============================================================================
-- Purpose:
--   Computes the fewest directed transfers between p_src and p_dst within
--   maximum depth bound p_k, restricting every account on the route to 'person'.
--
-- Optimization:
--   1. Replaces recursive CTE combinatorial state explosion with an iterative
--      level-by-level BFS loop.
--   2. Maintains a session-temporary visited table with PRIMARY KEY (acc) and
--      ON CONFLICT DO NOTHING to strictly prevent revisiting previously expanded
--      accounts across depths.
--   3. Evaluates destination presence immediately after inserting each depth level,
--      terminating early the moment the target is reached.
-- ============================================================================

CREATE OR REPLACE FUNCTION q7_v2(p_src int, p_dst int, p_k int) 
RETURNS int AS $$
DECLARE 
  d int := 0; 
  n int;
BEGIN
  -- Temporary table dropped at transaction/connection commit
  CREATE TEMP TABLE IF NOT EXISTS vis (
    acc int PRIMARY KEY, 
    depth int NOT NULL
  ) ON COMMIT DROP;

  TRUNCATE TABLE vis;

  -- Seed frontier with source account if it has role 'person'
  INSERT INTO vis 
  SELECT account_id, 0 
  FROM accounts 
  WHERE account_id = p_src AND role = 'person';
  
  GET DIAGNOSTICS n = ROW_COUNT;
  IF n = 0 THEN 
    RETURN NULL; 
  END IF;

  -- Trivial case: source is destination
  IF p_src = p_dst THEN 
    RETURN 0; 
  END IF;

  -- Level-by-level BFS expansion
  WHILE d < p_k LOOP
    INSERT INTO vis
      SELECT DISTINCT t.receiver_id, d + 1
      FROM vis v
      JOIN transfers t ON t.sender_id = v.acc
      JOIN accounts a ON a.account_id = t.receiver_id AND a.role = 'person'
      WHERE v.depth = d
    ON CONFLICT (acc) DO NOTHING;

    GET DIAGNOSTICS n = ROW_COUNT;
    d := d + 1;

    -- Early termination: check if destination was reached
    IF EXISTS (SELECT 1 FROM vis WHERE acc = p_dst) THEN 
      RETURN d; 
    END IF;

    -- No new frontier accounts reached: disconnected component
    IF n = 0 THEN 
      RETURN NULL; 
    END IF;
  END LOOP;

  -- Exceeded search bound p_k without reaching destination
  RETURN NULL;
END;
$$ LANGUAGE plpgsql;
