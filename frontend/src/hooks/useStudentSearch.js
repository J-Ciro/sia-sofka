import { useMemo } from 'react'

/**
 * Custom hook for filtering students by search term
 * @param {Array} students - Array of student objects
 * @param {string} searchTerm - Search term to filter by
 * @returns {Array} Filtered students
 */
export const useStudentSearch = (students, searchTerm) => {
  return useMemo(() => {
    if (!searchTerm.trim()) return students

    const normalizedSearch = searchTerm.toLowerCase()
    
    return students.filter(student => {
      const searchableText = `${student.nombre} ${student.apellido} ${student.codigo_institucional}`.toLowerCase()
      return searchableText.includes(normalizedSearch)
    })
  }, [students, searchTerm])
}
